"""Perguntas da conversa e a ordem em que são feitas.

A conversa começa aberta ("me conta o que aconteceu"). Do relato saem os campos
que der para entender; depois o Guardião só pergunta o que ainda falta, seguindo
o roteiro do tipo de remetente.
"""

from dataclasses import dataclass

from backend.graph.estado import Estado


@dataclass(frozen=True)
class Pergunta:
    id: str
    texto: str
    campo: str  # campo do estado que a resposta preenche


PERGUNTAS = {
    p.id: p
    for p in [
        Pergunta("relato", "Me conta o que aconteceu: quem falou com você e o que pediu?", "relato"),
        Pergunta(
            "remetente",
            "E quem foi que te procurou? Alguém da família, o banco, o INSS ou uma loja?",
            "remetente",
        ),
        Pergunta("numero_novo", "Essa pessoa está usando um número novo, que você não conhecia?", "numero_novo"),
        Pergunta("desculpa", "E ela explicou por que trocou de número?", "desculpa"),
        Pergunta("pedido_familia", "E o que ela pediu? Dinheiro, algum código, outra coisa?", "pedido"),
        Pergunta("pedido_banco", "E o que pediram? Sua senha, um código, ou para ligar em algum número?", "pedido"),
        Pergunta("link_inss", "Mandaram algum link, para prova de vida ou para atualizar o cadastro?", "pedido"),
        Pergunta("pedido_geral", "E o que pediram para você fazer?", "pedido"),
        Pergunta("urgencia", "Falaram que era urgente, ou fizeram alguma ameaça?", "urgencia"),
    ]
}

# Depois de saber quem procurou, cada remetente segue o seu roteiro.
ROTEIROS: dict[str, list[str]] = {
    "familia": ["numero_novo", "desculpa", "pedido_familia", "urgencia"],
    "banco": ["pedido_banco", "urgencia"],
    "inss": ["link_inss", "urgencia"],
    "loja": ["pedido_geral", "urgencia"],
    "outro": ["pedido_geral", "urgencia"],
}

# Uma palavra curta antes da próxima pergunta, variando para não soar como formulário.
CONFIRMACOES = ["Entendi.", "Certo.", "Tá bom."]


def _ja_sabe(estado: Estado, pergunta_id: str) -> bool:
    return pergunta_id in estado.get("respondidas", []) or estado.get(PERGUNTAS[pergunta_id].campo) is not None


def proxima_pergunta(estado: Estado) -> str | None:
    feitas = estado.get("respondidas", [])
    if "relato" not in feitas:
        return "relato"
    if estado.get("remetente") is None and "remetente" not in feitas:
        return "remetente"

    for pergunta_id in ROTEIROS[estado.get("remetente", "outro")]:
        if _ja_sabe(estado, pergunta_id):
            continue
        # A desculpa só ajuda quando foi preciso perguntar do número novo; se o relato
        # já contou tudo, perguntar de novo só atrasa o veredito.
        if pergunta_id == "desculpa" and not (estado.get("numero_novo") is True and "numero_novo" in feitas):
            continue
        # O falso sequestro chega por ligação: número novo e desculpa não ajudam.
        if pergunta_id in ("numero_novo", "desculpa") and estado.get("sequestro"):
            continue
        return pergunta_id
    return None


def texto_da_pergunta(estado: Estado, pergunta_id: str) -> str:
    """Texto falado: depois da primeira resposta, começa com uma confirmação curta."""
    texto = PERGUNTAS[pergunta_id].texto
    feitas = estado.get("respondidas", [])
    if not feitas:
        return texto
    return f"{CONFIRMACOES[(len(feitas) - 1) % len(CONFIRMACOES)]} {texto}"
