"""Traces no Langfuse: cada fala vira um trace, agrupados pela sessão da Alexa.

Desligado quando LANGFUSE_ENABLED não é "true" ou faltam as chaves.
"""

from functools import lru_cache

from backend import config


@lru_cache(maxsize=1)
def _handler():
    from langfuse.langchain import CallbackHandler

    return CallbackHandler()


def config_da_sessao(sessao_id: str) -> dict:
    """Config do LangGraph para uma conversa: thread_id e, se ligado, o Langfuse."""
    cfg = {"configurable": {"thread_id": sessao_id}, "run_name": "guardiao"}
    if config.langfuse_ativo():
        cfg["callbacks"] = [_handler()]
        cfg["metadata"] = {"langfuse_session_id": sessao_id}
    return cfg


def enviar_pendentes() -> None:
    """Envia os traces pendentes. Nunca chamar dentro da requisição da Alexa."""
    if config.langfuse_ativo():
        from langfuse import get_client

        get_client().flush()
