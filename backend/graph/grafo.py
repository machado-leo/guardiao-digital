"""Grafo de decisão em LangGraph.

    planejar ─┬─> perguntar ──> planejar      (enquanto houver pergunta)
              └─> avaliar ──> consultar_base ──> concluir ─┬─> avisar_familia ──> fim   (risco alto)
                                                           └─> fim

Cada pergunta pausa o grafo com interrupt(); a próxima fala do idoso retoma a
execução de onde parou. O estado de cada conversa fica no checkpointer, pela
chave thread_id (o sessionId da Alexa).
"""

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from backend.alerts.telegram import enviar_alerta, montar_mensagem
from backend.graph.estado import Estado
from backend.graph.interpretar import interpretar
from backend.graph.perguntas import PERGUNTAS, proxima_pergunta
from backend.graph.risco import avaliar_risco, deve_alertar, nivel
from backend.graph.veredito import redigir_veredito
from backend.rag.busca import buscar


def planejar(estado: Estado) -> dict:
    return {"proxima": proxima_pergunta(estado)}


def perguntar(estado: Estado) -> dict:
    pergunta_id = estado["proxima"]
    resposta = interrupt({"pergunta_id": pergunta_id, "texto": PERGUNTAS[pergunta_id].texto})
    return {
        **interpretar(pergunta_id, resposta),
        "respondidas": [*estado.get("respondidas", []), pergunta_id],
        "relato": [*estado.get("relato", []), resposta.strip()],
    }


def avaliar(estado: Estado) -> dict:
    risco, motivos = avaliar_risco(estado)
    return {"risco": risco, "motivos": motivos, "alertar": deve_alertar(risco)}


def consultar_base(estado: Estado) -> dict:
    # Sem risco não há golpe para citar; pula a busca e economiza tempo da Alexa.
    if nivel(estado["risco"]) == "baixo":
        return {"golpe": None}
    achado = buscar(estado)
    if achado is None:
        return {"golpe": None}
    golpe, distancia = achado
    return {
        "golpe": {
            "id": golpe.id,
            "nome": golpe.nome,
            "acao": golpe.acao,
            "fonte": golpe.fonte.nome,
            "url": golpe.fonte.url,
            "distancia": round(distancia, 3),
        }
    }


def concluir(estado: Estado) -> dict:
    return {"veredito": redigir_veredito(estado)}


def avisar_familia(estado: Estado) -> dict:
    texto = montar_mensagem(estado["risco"], estado["motivos"], estado.get("golpe"), estado["veredito"])
    return {"alerta_enviado": enviar_alerta(texto) is not None}


def _depois_de_planejar(estado: Estado) -> str:
    return "perguntar" if estado.get("proxima") else "avaliar"


def construir_grafo(checkpointer: BaseCheckpointSaver):
    grafo = StateGraph(Estado)
    grafo.add_node("planejar", planejar)
    grafo.add_node("perguntar", perguntar)
    grafo.add_node("avaliar", avaliar)
    grafo.add_node("consultar_base", consultar_base)
    grafo.add_node("concluir", concluir)
    grafo.add_node("avisar_familia", avisar_familia)

    grafo.add_edge(START, "planejar")
    grafo.add_conditional_edges("planejar", _depois_de_planejar, ["perguntar", "avaliar"])
    grafo.add_edge("perguntar", "planejar")
    grafo.add_edge("avaliar", "consultar_base")
    grafo.add_edge("consultar_base", "concluir")
    grafo.add_conditional_edges(
        "concluir", lambda estado: "avisar_familia" if estado["alertar"] else END, ["avisar_familia", END]
    )
    grafo.add_edge("avisar_familia", END)
    return grafo.compile(checkpointer=checkpointer)
