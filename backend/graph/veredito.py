"""Fala final: uma ou duas frases, tom calmo, uma ação clara.

Regra fixa: o Guardião nunca diz "pode pagar". Por isso a fala não é gerada pelo
GPT: quando a busca acha um golpe parecido na base, usa o nome e a ação escritos
à mão naquele caso; quando não acha, usa os modelos fixos abaixo.
"""

import re

from backend.graph.estado import Estado
from backend.graph.risco import nivel

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

# Senha ou código vindos de qualquer um que não seja o banco: em geral é a clonagem do WhatsApp.
SENHA_OU_CODIGO = (
    "Isso parece golpe. Nunca passe senha ou código que chegou no seu celular, "
    "nem para alguém da família. Ligue para a pessoa no número que você já conhece."
)

FALSO_SEQUESTRO = (
    "Isso parece o golpe do falso sequestro. Mantenha a calma e não fale o nome de ninguém. "
    "Desligue e ligue para o seu parente de outro telefone."
)

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


def _golpe_provavel(estado: Estado) -> str:
    remetente = estado.get("remetente", "outro")
    if estado.get("sequestro"):
        return FALSO_SEQUESTRO
    if estado.get("pedido") in ("senha", "codigo") and remetente != "banco":
        return SENHA_OU_CODIGO
    return GOLPE_PROVAVEL[remetente]


def redigir_veredito(estado: Estado) -> str:
    golpe = estado.get("golpe")
    match nivel(estado.get("risco", 0)):
        case "alto" if golpe:
            fala = f"Isso parece o {golpe['nome']}. {golpe['acao']}" + AVISO_FAMILIA
        case "alto":
            fala = _golpe_provavel(estado) + AVISO_FAMILIA
        case "medio" if golpe:
            fala = f"Essa mensagem tem sinais do {golpe['nome']}. {golpe['acao']}"
        case "medio":
            fala = SINAIS_DE_GOLPE
        case _:
            fala = SEM_SINAIS_FORTES
    return garantir_seguranca(fala)
