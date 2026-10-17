"""Perguntas curtas e a ordem em que são feitas para cada tipo de remetente."""

from dataclasses import dataclass

from backend.graph.estado import Estado


@dataclass(frozen=True)
class Pergunta:
    id: str
    texto: str


PERGUNTAS = {
    p.id: p
    for p in [
        Pergunta("remetente", "Quem te mandou a mensagem, ou quem ligou? Foi alguém da família, o banco, o INSS ou uma loja?"),
        Pergunta("numero_novo", "A pessoa está usando um número novo?"),
        Pergunta("desculpa", "E qual foi a desculpa para o número novo?"),
        Pergunta("pedido_familia", "E o que ela pediu? Foi dinheiro no PIX? Quanto?"),
        Pergunta("pedido_banco", "Pediram sua senha, algum código, ou para você ligar em algum número?"),
        Pergunta("link_inss", "Mandaram algum link para prova de vida ou recadastramento?"),
        Pergunta("pedido_geral", "O que pediram para você fazer? Pagar, clicar num link ou passar algum dado?"),
        Pergunta("urgencia", "Falaram que era urgente, ou ameaçaram alguma coisa?"),
    ]
}

# Depois de saber quem mandou, cada remetente segue o seu roteiro.
ROTEIROS: dict[str, list[str]] = {
    "familia": ["numero_novo", "desculpa", "pedido_familia", "urgencia"],
    "banco": ["pedido_banco", "urgencia"],
    "inss": ["link_inss", "urgencia"],
    "loja": ["pedido_geral", "urgencia"],
    "outro": ["pedido_geral", "urgencia"],
}


def proxima_pergunta(estado: Estado) -> str | None:
    feitas = estado.get("respondidas", [])
    if "remetente" not in feitas:
        return "remetente"

    for pergunta_id in ROTEIROS[estado.get("remetente", "outro")]:
        if pergunta_id in feitas:
            continue
        # Só faz sentido perguntar a desculpa se o número é novo.
        if pergunta_id == "desculpa" and estado.get("numero_novo") is not True:
            continue
        # O falso sequestro chega por ligação: número novo e desculpa não ajudam.
        if pergunta_id in ("numero_novo", "desculpa") and estado.get("sequestro"):
            continue
        return pergunta_id
    return None
