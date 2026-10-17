"""Pontuação de risco de 0 a 100, com uma regra simples de explicar na banca.

Primeira versão: os pesos ainda vão ser ajustados no tópico 3 do roadmap.
"""

from backend import config
from backend.graph.estado import Estado

PESO_PEDIDO = {"senha": 50, "codigo": 50, "pix": 30, "link": 30, "dados": 30, "ligar": 20}
PEDIDOS_SUSPEITOS = set(PESO_PEDIDO)


def avaliar_risco(estado: Estado) -> tuple[int, list[str]]:
    pontos = 0
    motivos = []
    pedido = estado.get("pedido")
    remetente = estado.get("remetente")

    if pedido in PESO_PEDIDO:
        pontos += PESO_PEDIDO[pedido]
        motivos.append(f"pediram {pedido}")
    if estado.get("numero_novo"):
        pontos += 30
        motivos.append("número novo")
    if estado.get("urgencia"):
        pontos += 20
        motivos.append("urgência ou ameaça")
    if remetente in ("banco", "inss") and pedido in PEDIDOS_SUSPEITOS:
        pontos += 20
        motivos.append(f"{remetente} não pede isso por mensagem")
    if remetente == "loja" and pedido in ("pix", "link"):
        pontos += 20
        motivos.append("cobrança por mensagem, fora do site da loja")
    if remetente == "familia" and estado.get("numero_novo") and pedido == "pix":
        pontos += 20
        motivos.append("padrão do golpe do falso parente")

    return min(pontos, 100), motivos


def deve_alertar(risco: int) -> bool:
    return risco >= config.limiar_alerta()
