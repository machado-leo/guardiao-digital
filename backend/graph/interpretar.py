"""Transforma a fala do idoso em campos do estado.

Primeiro tenta regras com palavras-chave, que são rápidas e previsíveis. O GPT só é
chamado quando as regras não resolvem, para não estourar o tempo da Alexa.
Na dúvida, as regras tendem para o lado mais seguro (mais risco, não menos).
"""

import re
import unicodedata
from functools import lru_cache

from backend import config
from backend.graph.perguntas import PERGUNTAS

REMETENTES = [
    ("familia", [r"filh[oa]s?", r"net[oa]s?", r"sobrinh[oa]s?", r"irma[o]?", r"genro", r"nora",
                 r"parentes?", r"familia", r"prim[oa]", r"marido", r"esposa", r"mae", r"pai"]),
    ("inss", [r"inss", r"aposentadoria", r"beneficio", r"previdencia"]),
    ("banco", [r"bancos?", r"caixa", r"bradesco", r"itau", r"santander", r"nubank", r"central",
               r"gerente", r"cartao"]),
    ("loja", [r"lojas?", r"correios", r"entregas?", r"frete", r"encomendas?", r"pacotes?", r"compras?",
              r"mercado livre", r"shopee", r"amazon"]),
    ("outro", [r"nao sei", r"nao conhec\w*", r"desconhecid[oa]", r"estranh[oa]"]),
]

# Ordem de prioridade: o pedido mais perigoso ganha quando aparecem vários.
PEDIDOS = [
    ("senha", [r"senhas?"]),
    ("codigo", [r"codigos?", r"token", r"numero que chegou"]),
    ("pix", [r"pix", r"transfer\w*", r"deposit\w*", r"dinheiro", r"reais", r"pag\w*", r"boleto", r"emprest\w*"]),
    ("link", [r"links?", r"clica\w*", r"cliqu\w*", r"sites?", r"aplicativos?", r"app", r"instal\w*", r"baix\w*"]),
    ("dados", [r"cpf", r"dados", r"documentos?", r"fotos?", r"cartao"]),
    ("ligar", [r"liga\w*", r"telefone"]),
]

# Checado antes dos pedidos: "não pediu nada, só mandou foto" não é pedido de dados.
NADA = [r"nao pediu nada", r"nao pediu", r"nada"]

SIM = [r"sim", r"ta", r"esta", r"estava", r"isso", r"uhum", r"aham", r"claro", r"pediu", r"mandou",
       r"falou", r"disse", r"positivo", r"exato", r"com certeza"]
NAO = [r"nao", r"nunca", r"nada", r"negativo", r"nem"]
DUVIDA = [r"nao sei", r"sei la", r"nao lembro", r"talvez"]

NUMERO_NOVO = [r"novo", r"trocou", r"outro numero", r"caiu", r"quebr\w*", r"perd\w*", r"roubad[oa]",
               r"nao tinha", r"nao conhec\w*"]
NUMERO_ANTIGO = [r"mesmo", r"de sempre", r"conhecido"]

URGENCIA = [r"urgen\w*", r"agora", r"hoje", r"rapido", r"prazo", r"bloque\w*", r"cancel\w*", r"cort\w*",
            r"pres[oa]", r"multa", r"amea\w*", r"senao"]


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _tem(texto: str, padroes: list[str]) -> bool:
    return re.search(r"\b(?:" + "|".join(padroes) + r")\b", texto) is not None


def _primeiro(texto: str, categorias: list[tuple[str, list[str]]]) -> str | None:
    return next((nome for nome, padroes in categorias if _tem(texto, padroes)), None)


def _sim_ou_nao(texto: str) -> bool | None:
    if _tem(texto, DUVIDA):
        return None
    if _tem(texto, NAO):
        return False
    if _tem(texto, SIM):
        return True
    return None


def extrair_valor(texto: str) -> int | None:
    """Valor em reais quando dito com algarismos ("400", "1.500", "2 mil")."""
    achado = re.search(r"(\d+(?:[.,]\d{3})*)(?:[.,]\d{1,2})?\s*(mil)?", texto)
    if achado:
        valor = int(re.sub(r"[.,]", "", achado.group(1)))
        return valor * 1000 if achado.group(2) else valor
    if _tem(texto, [r"mil"]):
        return 1000
    return None


@lru_cache(maxsize=1)
def _modelo():
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=config.modelo_openai(), timeout=4, max_retries=0)


def _classificar_com_llm(pergunta_id: str, resposta: str, opcoes: list[str]) -> str | None:
    """Pede ao GPT para escolher uma das opções. Devolve None se não der."""
    if not config.openai_configurado():
        return None
    prompt = (
        "Você classifica a resposta falada de uma pessoa idosa a uma pergunta de um assistente "
        "que ajuda a identificar golpes.\n"
        f"Pergunta: {PERGUNTAS[pergunta_id].texto}\n"
        f"Resposta: {resposta}\n"
        f"Responda apenas com uma destas opções, sem mais nada: {', '.join(opcoes)}"
    )
    try:
        saida = normalizar(str(_modelo().invoke(prompt).content)).strip(" .")
    except Exception:
        return None
    return saida if saida in opcoes else None


def _sim_ou_nao_com_llm(pergunta_id: str, resposta: str, texto: str) -> bool | None:
    if _tem(texto, DUVIDA):
        return None
    regra = _sim_ou_nao(texto)
    if regra is not None:
        return regra
    return {"sim": True, "nao": False}.get(_classificar_com_llm(pergunta_id, resposta, ["sim", "nao", "nao_sei"]))


def _pedido(pergunta_id: str, resposta: str, texto: str) -> dict:
    if _tem(texto, NADA):
        return {"pedido": "nada", "valor": None}
    valor = extrair_valor(texto)
    pedido = _primeiro(texto, PEDIDOS)
    if pedido is None and valor:
        pedido = "pix"
    if pedido is None:
        opcoes = [nome for nome, _ in PEDIDOS] + ["nada", "outro"]
        pedido = _classificar_com_llm(pergunta_id, resposta, opcoes) or "outro"
    return {"pedido": pedido, "valor": valor}


def interpretar(pergunta_id: str, resposta: str) -> dict:
    """Devolve os campos do estado preenchidos pela resposta a uma pergunta."""
    texto = normalizar(resposta)

    if pergunta_id == "remetente":
        opcoes = [nome for nome, _ in REMETENTES]
        remetente = _primeiro(texto, REMETENTES) or _classificar_com_llm(pergunta_id, resposta, opcoes)
        return {"remetente": remetente or "outro"}

    if pergunta_id == "numero_novo":
        if _tem(texto, NUMERO_NOVO):
            return {"numero_novo": True}
        if _tem(texto, NUMERO_ANTIGO):
            return {"numero_novo": False}
        return {"numero_novo": _sim_ou_nao_com_llm(pergunta_id, resposta, texto)}

    if pergunta_id == "desculpa":
        return {"desculpa": resposta.strip()[:200]}

    if pergunta_id == "link_inss":
        # "Sim" aqui quer dizer que mandaram link.
        if _primeiro(texto, PEDIDOS) is None and not _tem(texto, NADA):
            mandou = _sim_ou_nao_com_llm(pergunta_id, resposta, texto)
            return {"pedido": "nada" if mandou is False else "link", "valor": None}
        return _pedido(pergunta_id, resposta, texto)

    if pergunta_id in ("pedido_familia", "pedido_banco", "pedido_geral"):
        return _pedido(pergunta_id, resposta, texto)

    if pergunta_id == "urgencia":
        if _tem(texto, URGENCIA):
            return {"urgencia": True}
        return {"urgencia": _sim_ou_nao_com_llm(pergunta_id, resposta, texto)}

    raise ValueError(f"Pergunta desconhecida: {pergunta_id}")
