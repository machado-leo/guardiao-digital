"""Interface de conversa usada pela CLI e, depois, pelo endpoint da Alexa."""

from dataclasses import dataclass, field

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from backend import observabilidade
from backend.graph.grafo import construir_grafo

SAUDACAO = "Oi! Eu sou o Guardião. Vou te fazer umas perguntas rápidas. "


@dataclass
class Turno:
    fala: str
    encerrou: bool
    pergunta_id: str | None = None
    risco: int | None = None
    alertar: bool = False
    motivos: list[str] = field(default_factory=list)
    golpe: dict | None = None
    alerta_enviado: bool = False


class Guardiao:
    def __init__(self, checkpointer=None):
        self.grafo = construir_grafo(checkpointer or InMemorySaver())

    def iniciar(self, sessao_id: str) -> Turno:
        turno = self._executar(sessao_id, {})
        turno.fala = SAUDACAO + turno.fala
        return turno

    def responder(self, sessao_id: str, resposta: str) -> Turno:
        return self._executar(sessao_id, Command(resume=resposta))

    def _executar(self, sessao_id: str, entrada) -> Turno:
        resultado = self.grafo.invoke(entrada, observabilidade.config_da_sessao(sessao_id))

        if "__interrupt__" in resultado:
            pergunta = resultado["__interrupt__"][0].value
            return Turno(fala=pergunta["texto"], encerrou=False, pergunta_id=pergunta["pergunta_id"])

        return Turno(
            fala=resultado["veredito"],
            encerrou=True,
            risco=resultado["risco"],
            alertar=resultado["alertar"],
            motivos=resultado["motivos"],
            golpe=resultado.get("golpe"),
            alerta_enviado=resultado.get("alerta_enviado", False),
        )
