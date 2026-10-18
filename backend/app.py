"""Endpoint HTTPS que a skill da Alexa chama a cada fala.

    uvicorn backend.app:app --port 8000

A Alexa espera a resposta por uns 8 segundos. Os logs registram só o tipo de
requisição, a pergunta e o tempo gasto, nunca o que o idoso falou (LGPD).
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException

from backend import alexa, observabilidade
from backend.graph import Guardiao, Turno
from backend.graph.perguntas import PERGUNTAS

log = logging.getLogger("guardiao")
guardiao = Guardiao()


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not os.getenv("ALEXA_SKILL_ID"):
        log.warning("ALEXA_SKILL_ID vazio: aceitando requisições de qualquer skill (só para testes)")
    aquecer()
    yield
    # Envia os traces pendentes ao desligar, fora de qualquer requisição da Alexa.
    observabilidade.enviar_pendentes()


app = FastAPI(title="Guardião Digital", lifespan=ciclo_de_vida)


def aquecer() -> None:
    """Abre as conexões com a OpenAI antes da primeira fala: a primeira chamada leva ~3 s a mais."""
    from backend import config
    from backend.graph.fala import _modelo_pergunta
    from backend.rag.busca import buscar

    inicio = time.perf_counter()
    try:
        buscar({"remetente": "familia", "pedido": "pix", "relato": ["aquecimento"]})
    except Exception as erro:  # o servidor sobe mesmo sem OpenAI; a busca só é pulada
        log.warning("Aquecimento da busca falhou: %s", type(erro).__name__)
    if config.openai_configurado():
        # As perguntas têm só 2 s de limite: sem aquecer, a primeira cairia sempre na pronta.
        try:
            _modelo_pergunta().invoke("Responda só: ok", config={"run_name": "aquecimento"})
        except Exception as erro:
            log.warning("Aquecimento do GPT falhou: %s", type(erro).__name__)
    log.info("Aquecimento em %.2fs", time.perf_counter() - inicio)


@app.get("/saude")
def saude() -> dict:
    return {"ok": True}


def _validar(corpo: dict) -> None:
    esperado = os.getenv("ALEXA_SKILL_ID")
    if esperado and alexa.id_da_skill(corpo) != esperado:
        raise HTTPException(status_code=403, detail="Requisição de outra skill")
    if not alexa.timestamp_recente(corpo):
        raise HTTPException(status_code=400, detail="Timestamp fora da tolerância")


def _resposta_do_turno(sessao_id: str, turno: Turno) -> dict:
    if turno.encerrou:
        guardiao.encerrar(sessao_id)
        return alexa.resposta(turno.fala, encerrar=True)
    pergunta = PERGUNTAS[turno.pergunta_id].texto
    return alexa.resposta(turno.fala, encerrar=False, reprompt=alexa.FALA_REPROMPT + pergunta)


def _pergunta(fala: str, prefixo: str = "") -> dict:
    return alexa.resposta(prefixo + fala, encerrar=False, reprompt=alexa.FALA_REPROMPT + fala)


@app.post("/alexa")
def receber(corpo: dict = Body(...)) -> dict:
    _validar(corpo)
    inicio = time.perf_counter()
    sessao_id = corpo["session"]["sessionId"]
    requisicao = corpo["request"]
    tipo = requisicao["type"]
    intent = requisicao.get("intent", {})
    resultado = "?"
    # Vai para o trace do Langfuse: ajuda a ver qual intent capturou cada fala.
    contexto = {"origem": "alexa", "alexa_tipo": tipo, "alexa_intent": intent.get("name")}

    try:
        if tipo == "LaunchRequest":
            turno = guardiao.iniciar(sessao_id, contexto)
            resultado = turno.pergunta_id
            return _resposta_do_turno(sessao_id, turno)

        if tipo == "SessionEndedRequest":
            guardiao.encerrar(sessao_id)
            resultado = "sessao_encerrada"
            return alexa.resposta_vazia()

        if tipo != "IntentRequest":
            resultado = "ignorada"
            return alexa.resposta_vazia()

        if intent.get("name") in alexa.PARAR:
            guardiao.encerrar(sessao_id)
            resultado = "parou"
            return alexa.resposta(alexa.FALA_DESPEDIDA, encerrar=True)

        pendente = guardiao.pergunta_pendente(sessao_id)
        if pendente is None:
            # Chamada direta ("Alexa, pede pro Guardião...") ou sessão perdida: começa do zero.
            turno = guardiao.iniciar(sessao_id, contexto)
            pendente = PERGUNTAS[turno.pergunta_id].texto
            if alexa.texto_falado(intent) is None:
                resultado = turno.pergunta_id
                return _resposta_do_turno(sessao_id, turno)

        if intent.get("name") == alexa.AJUDA:
            resultado = "ajuda"
            return _pergunta(pendente, alexa.FALA_AJUDA)
        if intent.get("name") == alexa.REPETIR:
            resultado = "repetir"
            return _pergunta(pendente)

        texto = alexa.texto_falado(intent)
        if not texto:
            resultado = "nao_entendeu"
            return _pergunta(pendente, alexa.FALA_NAO_ENTENDI)

        turno = guardiao.responder(sessao_id, texto, contexto)
        resultado = "veredito" if turno.encerrou else turno.pergunta_id
        return _resposta_do_turno(sessao_id, turno)
    finally:
        log.info(
            "tipo=%s intent=%s resultado=%s %.2fs",
            tipo,
            intent.get("name", "-"),
            resultado,
            time.perf_counter() - inicio,
        )
