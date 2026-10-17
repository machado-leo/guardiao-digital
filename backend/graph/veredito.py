"""Falas prontas do veredito: uma ou duas frases, uma ação clara.

A fala começa pela gravidade e vai direto ao que fazer. O nome do golpe não entra:
para quem está sob pressão importa a ação, e o nome fica no trace e no alerta da família.

Estas falas são a referência que o GPT reescreve em backend/graph/fala.py e a
resposta de reserva quando o GPT demora ou sai das regras. Regra fixa: o Guardião
nunca diz "pode pagar".
"""

import re

from backend.graph.estado import Estado
from backend.graph.risco import PEDIDOS_SUSPEITOS, nivel

ALTO = "Atenção: isso tem muita cara de golpe."
MEDIO = "Cuidado: isso tem sinais de golpe."

GOLPE_PROVAVEL = {
    "familia": (
        "Atenção: isso tem muita cara de golpe. Não faça o PIX. "
        "Ligue agora para o número antigo da pessoa, aquele que você já tinha salvo."
    ),
    "banco": (
        "Atenção: isso tem muita cara de golpe. O banco nunca pede senha ou código por mensagem. "
        "Não passe nada e ligue para o número que está atrás do seu cartão."
    ),
    "inss": (
        "Atenção: isso tem muita cara de golpe. O INSS não manda link por mensagem. "
        "Não clique em nada. Se quiser conferir, ligue para o 135."
    ),
    "loja": (
        "Atenção: isso tem muita cara de golpe. Não pague e não clique em nada. "
        "Confira direto no site ou aplicativo da loja que você já usa."
    ),
    "outro": (
        "Atenção: isso tem muita cara de golpe. Não pague, não clique e não passe nenhum dado. "
        "Confirme com alguém de confiança antes de qualquer coisa."
    ),
}

# Senha ou código vindos de qualquer um que não seja o banco: em geral é a clonagem do WhatsApp.
SENHA_OU_CODIGO = (
    "Atenção: isso tem muita cara de golpe. Nunca passe senha ou código que chegou no seu celular, "
    "nem para alguém da família. Ligue para a pessoa no número que você já conhece."
)

FALSO_SEQUESTRO = (
    "Atenção: isso tem muita cara de golpe. Mantenha a calma e não fale o nome de ninguém. "
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

# Nada de dinheiro, dados, código ou link: não há o que confirmar, só tranquilizar.
SEM_SINAIS = (
    "Não vi sinais de golpe nessa situação. Se um dia pedirem dinheiro, senha ou código, "
    "confirme antes com alguém de confiança."
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


def orientacao(estado: Estado) -> str:
    """Fala pronta, sem o aviso à família."""
    golpe = estado.get("golpe")
    match nivel(estado.get("risco", 0)):
        case "alto" if golpe:
            return f"{ALTO} {golpe['acao']}"
        case "alto":
            return _golpe_provavel(estado)
        case "medio" if golpe:
            return f"{MEDIO} {golpe['acao']}"
        case "medio":
            return SINAIS_DE_GOLPE
        case _ if estado.get("pedido") in PEDIDOS_SUSPEITOS:
            return SEM_SINAIS_FORTES
        case _:
            return SEM_SINAIS


def com_aviso(estado: Estado, fala: str) -> str:
    """Acrescenta o aviso à família quando o risco é alto e passa pela checagem final."""
    if nivel(estado.get("risco", 0)) == "alto":
        fala += AVISO_FAMILIA
    return garantir_seguranca(fala)


def redigir_veredito(estado: Estado) -> str:
    return com_aviso(estado, orientacao(estado))
