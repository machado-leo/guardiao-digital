"""Base de golpes curada à mão, em data/golpes/golpes.json."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[2] / "data" / "golpes" / "golpes.json"


@dataclass(frozen=True)
class Fonte:
    nome: str
    url: str


@dataclass(frozen=True)
class Golpe:
    id: str
    nome: str  # sempre começa com "golpe", para encaixar em "Isso parece o {nome}."
    remetente: str
    pedidos: tuple[str, ...]
    descricao: str
    sinais: tuple[str, ...]
    acao: str  # o que o idoso deve fazer, numa ou duas frases curtas
    fonte: Fonte
    numero_novo: bool | None = None  # quando definido, o caso só vale com (ou sem) número novo

    def texto_para_busca(self) -> str:
        return f"{self.nome}. {self.descricao} Sinais: {'; '.join(self.sinais)}."


def carregar(arquivo: Path = ARQUIVO) -> list[Golpe]:
    with arquivo.open(encoding="utf-8") as f:
        casos = json.load(f)
    return [
        Golpe(
            id=caso["id"],
            nome=caso["nome"],
            remetente=caso["remetente"],
            pedidos=tuple(caso["pedidos"]),
            descricao=caso["descricao"],
            sinais=tuple(caso["sinais"]),
            acao=caso["acao"],
            fonte=Fonte(**caso["fonte"]),
            numero_novo=caso.get("numero_novo"),
        )
        for caso in casos
    ]


@lru_cache(maxsize=1)
def por_id() -> dict[str, Golpe]:
    return {golpe.id: golpe for golpe in carregar()}
