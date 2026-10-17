"""Pontuação de risco de 0 a 100: a soma dos sinais de golpe presentes na conversa.

Cada sinal tem pontos fixos e um motivo legível, para dar para explicar na banca
por que uma conversa recebeu aquela nota. Faixas:

    baixo  0 a 39          "não vi sinais fortes", mas manda confirmar mesmo assim
    medio  40 até o limiar "tem sinais de golpe", confirme por outro caminho
    alto   limiar a 100    golpe provável e alerta à família (RISK_ALERT_THRESHOLD, padrão 70)
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from backend import config
from backend.graph.estado import Estado

RISCO_MEDIO = 40

Nivel = Literal["baixo", "medio", "alto"]

PEDIDOS_SUSPEITOS = {"senha", "codigo", "pix", "link", "dados", "ligar"}
INSTITUICOES = {"banco", "inss", "loja"}


@dataclass(frozen=True)
class Sinal:
    motivo: str
    pontos: int
    presente: Callable[[Estado], bool]


def _pediu(*pedidos: str) -> Callable[[Estado], bool]:
    return lambda estado: estado.get("pedido") in pedidos


SINAIS = [
    # Ninguém legítimo pede senha ou código: sozinho, já aciona o alerta.
    Sinal("pediram senha ou código", 70, _pediu("senha", "codigo")),
    Sinal("pediram PIX ou pagamento", 30, _pediu("pix")),
    Sinal("pediram para clicar em link ou instalar aplicativo", 30, _pediu("link")),
    Sinal("pediram dados pessoais", 30, _pediu("dados")),
    Sinal("pediram para ligar em outro número", 30, _pediu("ligar")),
    Sinal("número novo", 30, lambda e: e.get("numero_novo") is True),
    Sinal("urgência ou ameaça", 20, lambda e: e.get("urgencia") is True),
    Sinal("pedido de resgate, padrão do falso sequestro", 30, lambda e: e.get("sequestro") is True),
    # Banco, INSS e loja não pedem nada disso por mensagem.
    Sinal(
        "instituição pedindo isso por mensagem",
        30,
        lambda e: e.get("remetente") in INSTITUICOES and e.get("pedido") in PEDIDOS_SUSPEITOS,
    ),
    Sinal(
        "remetente desconhecido pedindo algo",
        20,
        lambda e: e.get("remetente") == "outro" and e.get("pedido") in PEDIDOS_SUSPEITOS,
    ),
    # Febraban: "sempre desconfie" de pedido de dinheiro de parente por mensagem,
    # mesmo do número de sempre (o WhatsApp pode ter sido clonado).
    Sinal(
        "parente pedindo dinheiro por mensagem",
        10,
        lambda e: e.get("remetente") == "familia" and e.get("pedido") == "pix",
    ),
    Sinal(
        "padrão do golpe do falso parente",
        20,
        lambda e: e.get("remetente") == "familia" and e.get("numero_novo") is True and e.get("pedido") == "pix",
    ),
]


def avaliar_risco(estado: Estado) -> tuple[int, list[str]]:
    presentes = [sinal for sinal in SINAIS if sinal.presente(estado)]
    pontos = sum(sinal.pontos for sinal in presentes)
    return min(pontos, 100), [sinal.motivo for sinal in presentes]


def nivel(risco: int) -> Nivel:
    if risco >= config.limiar_alerta():
        return "alto"
    if risco >= RISCO_MEDIO:
        return "medio"
    return "baixo"


def deve_alertar(risco: int) -> bool:
    return nivel(risco) == "alto"
