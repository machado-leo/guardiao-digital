"""Transforma a fala do idoso em campos do estado.

Primeiro tenta regras com palavras-chave, que são rápidas e previsíveis. O GPT só é
chamado quando as regras não resolvem, para não estourar o tempo da Alexa.
Na dúvida, as regras tendem para o lado mais seguro (mais risco, não menos).
"""

import json
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
    # "pelo aplicativo" é só o canal; pedir para instalar ou baixar é que é suspeito.
    ("link", [r"links?", r"clica\w*", r"cliqu\w*", r"sites?", r"instal\w*", r"baix\w*"]),
    ("dados", [r"cpf", r"dados", r"documentos?", r"fotos?", r"cartao"]),
    # "ligaram" conta como o canal, não como pedido; só "ligar para..." é pedido.
    ("ligar", [r"ligar", r"ligue", r"telefone", r"0800", r"zero oitocentos"]),
]

# Checado antes dos pedidos: "não pediu nada, só mandou foto" não é pedido de dados.
NADA = [r"nao pediu nada", r"nao pediu", r"nada", r"nenhum\w*"]
# No relato, "nada" sozinho aparece em outras frases ("não aconteceu nada, só o banco ligou").
NADA_NO_RELATO = [r"nao pediu"]

# Relatos curtos ("meu filho") não justificam esperar o GPT; as perguntas seguintes completam.
PALAVRAS_PARA_USAR_GPT = 4

SIM = [r"sim", r"ta", r"esta", r"estava", r"isso", r"uhum", r"aham", r"claro", r"pediu", r"mandou",
       r"falou", r"disse", r"positivo", r"exato", r"com certeza"]
NAO = [r"nao", r"nunca", r"nada", r"negativo", r"nem"]
DUVIDA = [r"nao sei", r"sei la", r"nao lembro", r"talvez"]
# Na urgência, "falou que precisa para..." não é um sim: verbos de fala só valem para pedidos.
SIM_EXPLICITO = [r"sim", r"isso", r"uhum", r"aham", r"claro", r"positivo", r"exato", r"com certeza", r"foi sim"]

NUMERO_NOVO = [r"novo", r"trocou", r"outro numero", r"caiu", r"quebr\w*", r"perd\w*", r"roubad[oa]",
               r"nao tinha", r"nao conhec\w*"]
NUMERO_ANTIGO = [r"mesmo", r"de sempre", r"conhecido"]

URGENCIA = [r"urgen\w*", r"agora", r"hoje", r"rapido", r"prazo", r"bloque\w*", r"cancel\w*", r"cort\w*",
            r"pres[oa]", r"multa", r"amea\w*", r"senao", r"nao deslig\w*", r"resgate", r"machuc\w*",
            r"sequestr\w*"]

# Detectado em qualquer resposta: muda o roteiro e pesa no risco.
SEQUESTRO = [r"sequestr\w*", r"resgate", r"refem", r"voz chorando"]


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _tem(texto: str, padroes: list[str]) -> bool:
    return re.search(r"\b(?:" + "|".join(padroes) + r")\b", texto) is not None


def _primeiro(texto: str, categorias: list[tuple[str, list[str]]]) -> str | None:
    return next((nome for nome, padroes in categorias if _tem(texto, padroes)), None)


def _sim_ou_nao(texto: str, sim: list[str] = SIM) -> bool | None:
    if _tem(texto, DUVIDA):
        return None
    if _tem(texto, NAO):
        return False
    if _tem(texto, sim):
        return True
    return None


# A Alexa transcreve "um" e "uma" como "1": valores pequenos não contam como dinheiro.
VALOR_MINIMO = 10
NUMERO = re.compile(r"(r\$\s*)?(\d+(?:[.,]\d{3})*)(?:[.,]\d{1,2})?\s*(mil\b)?")
PALAVRA_DE_DINHEIRO = re.compile(r"\s*(?:reais|real|conto|contos|pila)\b")


def extrair_valor(texto: str, exigir_moeda: bool = False) -> int | None:
    """Valor em reais quando dito com algarismos ("400", "1.500", "2 mil", "R$ 500").

    No relato livre, exigir_moeda pede "reais", "mil" ou "R$" junto, porque números
    soltos ali costumam ser outra coisa ("1 carta", "1 número").
    """
    for achado in NUMERO.finditer(texto):
        simbolo, digitos, mil = achado.groups()
        tem_moeda = bool(simbolo or mil or PALAVRA_DE_DINHEIRO.match(texto, achado.end()))
        if exigir_moeda and not tem_moeda:
            continue
        valor = int(re.sub(r"[.,]", "", digitos)) * (1000 if mil else 1)
        if valor >= VALOR_MINIMO:
            return valor
    if _tem(texto, [r"mil reais"] if exigir_moeda else [r"mil"]):
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
        saida = normalizar(str(_modelo().invoke(prompt, config={"run_name": f"classificar_{pergunta_id}"}).content)).strip(" .")
    except Exception:
        return None
    return saida if saida in opcoes else None


def _sim_ou_nao_com_llm(pergunta_id: str, resposta: str, texto: str, sim: list[str] = SIM) -> bool | None:
    if _tem(texto, DUVIDA):
        return None
    regra = _sim_ou_nao(texto, sim)
    if regra is not None:
        return regra
    return {"sim": True, "nao": False}.get(_classificar_com_llm(pergunta_id, resposta, ["sim", "nao", "nao_sei"]))


# "nada" fica de fora: o GPT tende a responder "nada" quando o relato só não citou o
# pedido, e isso pularia a pergunta e baixaria o risco. Só as regras marcam "nada".
VALORES_DO_RELATO = {
    "remetente": {nome for nome, _ in REMETENTES},
    "pedido": {nome for nome, _ in PEDIDOS},
    "numero_novo": {True, False},
    "urgencia": {True, False},
}


def _extrair_com_llm(resposta: str) -> dict:
    """Pede ao GPT os campos de um relato livre, numa chamada só. {} se não der."""
    if not config.openai_configurado():
        return {}
    prompt = (
        "Você extrai informações do relato falado de uma pessoa idosa que recebeu uma mensagem "
        "ou ligação suspeita. O texto vem da transcrição da Alexa e pode ter palavras erradas.\n"
        f"Relato: {resposta}\n"
        "Responda só com um JSON com estas chaves, usando null quando o relato não disser:\n"
        '- "remetente": "familia", "banco", "inss", "loja" ou "outro"\n'
        '- "pedido": "senha", "codigo", "pix", "link", "dados" ou "ligar"\n'
        '- "numero_novo": true ou false (se a pessoa usa um número que o idoso não conhecia)\n'
        '- "urgencia": true ou false (se houve pressa, prazo ou ameaça)'
    )
    try:
        saida = str(_modelo().invoke(prompt, config={"run_name": "interpretar_relato"}).content)
        dados = json.loads(saida[saida.index("{") : saida.rindex("}") + 1])
    except Exception:
        return {}
    campos = {campo: dados[campo] for campo, validos in VALORES_DO_RELATO.items() if dados.get(campo) in validos}
    # Do GPT só vale o "sim": um "não" para urgência ou número novo costuma ser só
    # o relato não ter falado disso, e aceitar pularia a pergunta e baixaria o risco.
    return {campo: valor for campo, valor in campos.items() if valor is not False}


def _relato(resposta: str, texto: str) -> dict:
    """Tira do relato livre tudo o que der; o que faltar vira pergunta depois."""
    campos = {}
    if remetente := _primeiro(texto, REMETENTES):
        campos["remetente"] = remetente
    if _tem(texto, NADA_NO_RELATO):
        campos["pedido"] = "nada"
    elif pedido := _primeiro(texto, PEDIDOS) or ("pix" if extrair_valor(texto, exigir_moeda=True) else None):
        campos.update(pedido=pedido, valor=extrair_valor(texto, exigir_moeda=True))
    if _tem(texto, NUMERO_NOVO):
        campos["numero_novo"] = True
    elif _tem(texto, NUMERO_ANTIGO):
        campos["numero_novo"] = False
    if _tem(texto, URGENCIA):
        campos["urgencia"] = True

    falta_o_essencial = "remetente" not in campos or "pedido" not in campos
    if falta_o_essencial and len(texto.split()) >= PALAVRAS_PARA_USAR_GPT:
        for campo, valor in _extrair_com_llm(resposta).items():
            campos.setdefault(campo, valor)
    return campos


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
    campos = _interpretar_pergunta(pergunta_id, resposta, normalizar(resposta))
    if _tem(normalizar(resposta), SEQUESTRO):
        campos["sequestro"] = True
    return campos


def _interpretar_pergunta(pergunta_id: str, resposta: str, texto: str) -> dict:
    if pergunta_id == "relato":
        return _relato(resposta, texto)

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
        return {"urgencia": _sim_ou_nao_com_llm(pergunta_id, resposta, texto, SIM_EXPLICITO)}

    raise ValueError(f"Pergunta desconhecida: {pergunta_id}")
