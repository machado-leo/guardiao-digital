"""Traces no Langfuse: cada fala vira um trace, agrupados pela sessão da Alexa.

Desligado quando LANGFUSE_ENABLED não é "true" ou faltam as chaves.
"""

from functools import lru_cache

from backend import config
from backend.privacidade import mascarar


@lru_cache(maxsize=1)
def _handler():
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler

    # O cliente criado aqui, com a máscara, é o que o CallbackHandler passa a usar.
    Langfuse(mask=mascarar if config.langfuse_mascarar() else None)
    return CallbackHandler()


def config_da_sessao(sessao_id: str, contexto: dict | None = None) -> dict:
    """Config do LangGraph para uma conversa: thread_id e, se ligado, o Langfuse.

    contexto vai como metadata do trace (por exemplo, o intent da Alexa daquela fala);
    a chave "origem" ("alexa" ou "cli") vira tag, para filtrar no Langfuse.
    """
    cfg = {"configurable": {"thread_id": sessao_id}, "run_name": "guardiao"}
    if config.langfuse_ativo():
        contexto = contexto or {}
        cfg["callbacks"] = [_handler()]
        cfg["metadata"] = {
            "langfuse_session_id": sessao_id,
            "langfuse_tags": [contexto.get("origem", "desconhecida")],
            **contexto,
        }
    return cfg


def registrar_resultado(sessao_id: str, resultado: dict) -> None:
    """Grava o desfecho da conversa como scores da sessão, para filtrar e comparar no Langfuse."""
    if not config.langfuse_ativo():
        return
    from langfuse import get_client

    from backend.graph.risco import nivel

    cliente = get_client()
    golpe = resultado.get("golpe") or {}
    cliente.create_score(name="risco", value=resultado["risco"], session_id=sessao_id, data_type="NUMERIC")
    cliente.create_score(name="nivel", value=nivel(resultado["risco"]), session_id=sessao_id, data_type="CATEGORICAL")
    cliente.create_score(
        name="alerta_familia", value=1 if resultado["alertar"] else 0, session_id=sessao_id, data_type="BOOLEAN"
    )
    cliente.create_score(
        name="golpe_parecido", value=golpe.get("id", "nenhum"), session_id=sessao_id, data_type="CATEGORICAL"
    )
    cliente.create_score(
        name="perguntas", value=len(resultado.get("respondidas", [])), session_id=sessao_id, data_type="NUMERIC"
    )
    cliente.create_score(
        name="origem_da_fala",
        value=resultado.get("origem_da_fala", "?"),
        session_id=sessao_id,
        data_type="CATEGORICAL",
    )


def enviar_pendentes() -> None:
    """Envia os traces pendentes. Nunca chamar dentro da requisição da Alexa."""
    if config.langfuse_ativo():
        from langfuse import get_client

        get_client().flush()
