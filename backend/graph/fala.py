"""Fala final escrita pelo GPT, a partir de uma decisão que ele não toma.

As regras e a base de golpes já decidiram o nível de risco e se a família será
avisada. O GPT só reescreve a orientação pronta de um jeito que converse com o que
a pessoa contou. Se ele demorar, quebrar alguma regra ou não estiver configurado,
vale a fala pronta de backend/graph/veredito.py.
"""

import re
from functools import lru_cache

from backend import config
from backend.graph.estado import Estado
from backend.graph.risco import PEDIDOS_SUSPEITOS, nivel
from backend.graph.veredito import AUTORIZA_PAGAMENTO, com_aviso, orientacao

# O veredito já gasta tempo com a busca na base; acima disso a Alexa fica arriscada.
TIMEOUT = 3
TAMANHO = (20, 280)

SITUACAO = {
    "alto": "risco alto: é muito provavelmente golpe. O sistema avisa a família sozinho, não fale disso.",
    "medio": "risco médio: há sinais de golpe. A pessoa deve confirmar por outro caminho antes de qualquer coisa.",
    "baixo": (
        "risco baixo: não há sinais fortes de golpe, mas pediram dinheiro, dados, código ou link. "
        "Tranquilize a pessoa e lembre de confirmar com quem mandou antes de atender o pedido."
    ),
    "sem_pedido": (
        "sem sinais de golpe: ninguém pediu dinheiro, dados, código nem link. Tranquilize a pessoa, "
        "sem desconfiança. Não diga que é garantido; no máximo lembre, numa frase curta, que se um dia "
        "pedirem dinheiro, senha ou código, é bom confirmar antes."
    ),
}

CITA_NOME_DE_GOLPE = re.compile(r"golpe d[oa]s? ", re.IGNORECASE)
# Tranquilizar pode; garantir que não é golpe, não.
DIZ_QUE_E_SEGURO = re.compile(r"(é seguro|pode confiar|não é golpe|com certeza não)", re.IGNORECASE)


def _situacao(estado: Estado) -> str:
    atual = nivel(estado.get("risco", 0))
    if atual == "baixo" and estado.get("pedido") not in PEDIDOS_SUSPEITOS:
        return "sem_pedido"
    return atual


@lru_cache(maxsize=1)
def _modelo():
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=config.modelo_openai(), timeout=TIMEOUT, max_retries=0)


def _prompt(estado: Estado, referencia: str) -> str:
    return (
        "Você é o Guardião, um assistente de voz que ajuda pessoas idosas a perceber golpes. "
        "Escreva o que a Alexa vai falar agora, em português do Brasil.\n\n"
        f"Situação: {SITUACAO[_situacao(estado)]}\n"
        f"O que a pessoa contou: {' / '.join(estado.get('relato', []))}\n"
        f"Sinais encontrados: {', '.join(estado.get('motivos', [])) or 'nenhum'}\n"
        f"Orientação de referência: {referencia}\n\n"
        "Regras:\n"
        "- No máximo duas frases curtas, tom calmo e acolhedor, sem termos técnicos.\n"
        "- Mantenha a ação da orientação de referência, com suas palavras e sem mudar o sentido.\n"
        "- Pode se referir ao que a pessoa contou, sem inventar nada que ela não disse.\n"
        "- Nunca diga que ela pode pagar, transferir ou passar dados, nem que é seguro.\n"
        "- Não diga o nome de nenhum golpe. Sem emojis, listas ou aspas.\n"
        "Responda só com a fala."
    )


def aceitavel(fala: str, estado: Estado) -> bool:
    if not TAMANHO[0] <= len(fala) <= TAMANHO[1]:
        return False
    if AUTORIZA_PAGAMENTO.search(fala) or CITA_NOME_DE_GOLPE.search(fala) or DIZ_QUE_E_SEGURO.search(fala):
        return False
    # Com risco, a fala precisa mandar não fazer algo; com pedido e risco baixo, confirmar antes.
    match _situacao(estado):
        case "sem_pedido":
            return True
        case "baixo":
            return "confirm" in fala.lower()
        case _:
            return "não" in fala.lower()


def escrever(estado: Estado) -> tuple[str, str]:
    """Devolve a fala e de onde ela veio: "gpt", ou o motivo de ter usado a pronta."""
    referencia = orientacao(estado)
    if not config.openai_configurado():
        return com_aviso(estado, referencia), "pronta"
    try:
        resposta = _modelo().invoke(_prompt(estado, referencia), config={"run_name": "escrever_fala"})
        fala = str(resposta.content).strip().strip('"')
    except Exception:
        return com_aviso(estado, referencia), "pronta: gpt falhou ou demorou"
    if not aceitavel(fala, estado):
        return com_aviso(estado, referencia), "pronta: gpt quebrou uma regra"
    return com_aviso(estado, fala), "gpt"
