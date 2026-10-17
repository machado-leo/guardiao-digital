"""Grafo de decisão em LangGraph.

    planejar ─┬─> perguntar ──> planejar      (enquanto houver pergunta)
              └─> avaliar ──> concluir ──> fim

Cada pergunta pausa o grafo com interrupt(); a próxima fala do idoso retoma a
execução de onde parou. O estado de cada conversa fica no checkpointer, pela
chave thread_id (o sessionId da Alexa).
"""

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from backend.graph.estado import Estado
from backend.graph.interpretar import interpretar
from backend.graph.perguntas import PERGUNTAS, proxima_pergunta
from backend.graph.risco import avaliar_risco, deve_alertar
from backend.graph.veredito import redigir_veredito


def planejar(estado: Estado) -> dict:
    return {"proxima": proxima_pergunta(estado)}


def perguntar(estado: Estado) -> dict:
    pergunta_id = estado["proxima"]
    resposta = interrupt({"pergunta_id": pergunta_id, "texto": PERGUNTAS[pergunta_id].texto})
    return {
        **interpretar(pergunta_id, resposta),
        "respondidas": [*estado.get("respondidas", []), pergunta_id],
    }


def avaliar(estado: Estado) -> dict:
    risco, motivos = avaliar_risco(estado)
    return {"risco": risco, "motivos": motivos, "alertar": deve_alertar(risco)}


def concluir(estado: Estado) -> dict:
    return {"veredito": redigir_veredito(estado)}


def _depois_de_planejar(estado: Estado) -> str:
    return "perguntar" if estado.get("proxima") else "avaliar"


def construir_grafo(checkpointer: BaseCheckpointSaver):
    grafo = StateGraph(Estado)
    grafo.add_node("planejar", planejar)
    grafo.add_node("perguntar", perguntar)
    grafo.add_node("avaliar", avaliar)
    grafo.add_node("concluir", concluir)

    grafo.add_edge(START, "planejar")
    grafo.add_conditional_edges("planejar", _depois_de_planejar, ["perguntar", "avaliar"])
    grafo.add_edge("perguntar", "planejar")
    grafo.add_edge("avaliar", "concluir")
    grafo.add_edge("concluir", END)
    return grafo.compile(checkpointer=checkpointer)
