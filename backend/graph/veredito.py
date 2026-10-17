"""Fala final: uma ou duas frases, tom calmo, uma ação clara.

Regra fixa: o Guardião nunca diz "pode pagar". As falas são modelos fixos para
garantir isso; a redação com GPT e a citação da base de golpes entram com o RAG.
"""

import re

from backend.graph.estado import Estado

RISCO_MEDIO = 40

GOLPE_PROVAVEL = {
    "familia": (
        "Isso parece um golpe muito comum, o do falso parente. Não faça o PIX. "
        "Ligue agora para o número antigo da pessoa, aquele que você já tinha salvo."
    ),
    "banco": (
        "Isso parece golpe. O banco nunca pede senha ou código por mensagem. "
        "Não passe nada e ligue para o número que está atrás do seu cartão."
    ),
    "inss": (
        "Isso parece golpe. O INSS não manda link por mensagem. "
        "Não clique em nada. Se quiser conferir, ligue para o 135."
    ),
    "loja": (
        "Isso parece golpe. Não pague e não clique em nada. "
        "Confira direto no site ou aplicativo da loja que você já usa."
    ),
    "outro": (
        "Isso parece golpe. Não pague, não clique e não passe nenhum dado. "
        "Confirme com alguém de confiança antes de qualquer coisa."
    ),
}

SINAIS_DE_GOLPE = (
    "Essa mensagem tem sinais de golpe. Antes de fazer qualquer coisa, "
    "confirme por outro caminho, ligando para um número que você já conhece."
)

SEM_SINAIS_FORTES = (
    "Não vi sinais fortes de golpe. Mesmo assim, não pague nada "
    "antes de confirmar por outro caminho com quem mandou."
)

AVISO_FAMILIA = " Vou avisar sua família para te ligar também."

# Rede de segurança caso alguma fala futura (ou o GPT) tente autorizar pagamento.
AUTORIZA_PAGAMENTO = re.compile(r"pode (pagar|fazer o pix|transferir|mandar o dinheiro)", re.IGNORECASE)


def garantir_seguranca(fala: str) -> str:
    return SINAIS_DE_GOLPE if AUTORIZA_PAGAMENTO.search(fala) else fala


def redigir_veredito(estado: Estado) -> str:
    risco = estado.get("risco", 0)
    if estado.get("alertar"):
        fala = GOLPE_PROVAVEL[estado.get("remetente", "outro")] + AVISO_FAMILIA
    elif risco >= RISCO_MEDIO:
        fala = SINAIS_DE_GOLPE
    else:
        fala = SEM_SINAIS_FORTES
    return garantir_seguranca(fala)
