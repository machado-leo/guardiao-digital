"""Interface de conversa usada pela CLI e, depois, pelo endpoint da Alexa."""

import random
from dataclasses import dataclass, field

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from backend import observabilidade
from backend.graph.grafo import construir_grafo
from backend.graph.perguntas import ABERTURAS



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
        self.checkpointer = checkpointer or InMemorySaver()
        self.grafo = construir_grafo(self.checkpointer)

    def pergunta_pendente(self, sessao_id: str) -> str | None:
        """Texto da pergunta que está esperando resposta; None se a conversa não está em andamento."""
        estado = self.grafo.get_state({"configurable": {"thread_id": sessao_id}})
        for tarefa in estado.tasks:
            for pausa in tarefa.interrupts:
                return pausa.value["texto"]
        return None

    def encerrar(self, sessao_id: str) -> None:
        """Apaga a memória da conversa: nada da sessão fica guardado depois que ela acaba."""
        self.checkpointer.delete_thread(sessao_id)

    def iniciar(self, sessao_id: str, contexto: dict | None = None) -> Turno:
        turno = self._executar(sessao_id, {}, contexto)
        turno.fala = random.choice(ABERTURAS)
        return turno

    def responder(self, sessao_id: str, resposta: str, contexto: dict | None = None) -> Turno:
        return self._executar(sessao_id, Command(resume=resposta), contexto)

    def _executar(self, sessao_id: str, entrada, contexto: dict | None = None) -> Turno:
        resultado = self.grafo.invoke(entrada, observabilidade.config_da_sessao(sessao_id, contexto))

        if "__interrupt__" in resultado:
            pergunta = resultado["__interrupt__"][0].value
            return Turno(fala=pergunta["texto"], encerrou=False, pergunta_id=pergunta["pergunta_id"])

        observabilidade.registrar_resultado(sessao_id, resultado)
        return Turno(
            fala=resultado["veredito"],
            encerrou=True,
            risco=resultado["risco"],
            alertar=resultado["alertar"],
            motivos=resultado["motivos"],
            golpe=resultado.get("golpe"),
            alerta_enviado=resultado.get("alerta_enviado", False),
        )
