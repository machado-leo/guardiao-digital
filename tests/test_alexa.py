"""Requisições no formato da Alexa, do jeito que o console de testes manda."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.privacidade import mascarar

SKILL = "amzn1.ask.skill.teste"


@pytest.fixture(autouse=True)
def skill_configurada(monkeypatch):
    monkeypatch.setenv("ALEXA_SKILL_ID", SKILL)


@pytest.fixture
def cliente():
    return TestClient(app)


def requisicao(sessao: str, tipo: str, intent: str | None = None, fala: str | None = None, **extra) -> dict:
    corpo = {
        "version": "1.0",
        "session": {"new": tipo == "LaunchRequest", "sessionId": sessao, "application": {"applicationId": SKILL}},
        "context": {"System": {"application": {"applicationId": SKILL}}},
        "request": {
            "type": tipo,
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "locale": "pt-BR",
        },
    }
    if intent:
        slots = {"resposta": {"name": "resposta", "value": fala}} if fala else {}
        corpo["request"]["intent"] = {"name": intent, "slots": slots}
    corpo["request"].update(extra)
    return corpo


def falar(cliente, sessao, fala):
    return cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "RespostaIntent", fala)).json()


def texto(resposta: dict) -> str:
    return resposta["response"]["outputSpeech"]["text"]


def test_conversa_completa_pela_alexa(cliente):
    sessao = str(uuid.uuid4())
    abertura = cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest")).json()
    assert "aconte" in texto(abertura).lower()
    assert abertura["response"]["shouldEndSession"] is False
    assert "reprompt" in abertura["response"]

    falar(cliente, sessao, "meu filho")
    falar(cliente, sessao, "tá, disse que o celular caiu na água")
    falar(cliente, sessao, "que perdeu o celular")
    falar(cliente, sessao, "pediu 400 reais no pix")
    final = falar(cliente, sessao, "disse que era urgente")

    assert "Não faça o PIX" in texto(final)
    assert final["response"]["shouldEndSession"] is True
    assert "reprompt" not in final["response"]


def test_sim_e_nao_dos_intents_prontos(cliente):
    sessao = str(uuid.uuid4())
    cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest"))
    falar(cliente, sessao, "meu neto")
    resposta = cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "AMAZON.NoIntent")).json()
    assert "o que ela pediu" in texto(resposta).lower()


def test_nao_entendeu_repete_a_pergunta(cliente):
    sessao = str(uuid.uuid4())
    cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest"))
    resposta = cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "AMAZON.FallbackIntent")).json()
    assert texto(resposta).startswith("Desculpe, não entendi. Me conta o que aconteceu")
    assert resposta["response"]["shouldEndSession"] is False


def test_ajuda_e_repetir(cliente):
    sessao = str(uuid.uuid4())
    cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest"))
    ajuda = cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "AMAZON.HelpIntent")).json()
    assert "Me conta o que aconteceu" in texto(ajuda)
    repetir = cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "AMAZON.RepeatIntent")).json()
    assert texto(repetir).startswith("Me conta o que aconteceu")


def test_parar_encerra_sem_autorizar_pagamento(cliente):
    sessao = str(uuid.uuid4())
    cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest"))
    resposta = cliente.post("/alexa", json=requisicao(sessao, "IntentRequest", "AMAZON.StopIntent")).json()
    assert resposta["response"]["shouldEndSession"] is True
    assert "não pague nada" in texto(resposta)


def test_chamada_direta_sem_abrir_a_skill(cliente):
    # "Alexa, pede pro Guardião..." chega como IntentRequest numa sessão nova.
    resposta = falar(cliente, str(uuid.uuid4()), "foi o banco")
    assert "senha" in texto(resposta)


def test_sessao_encerrada_apaga_a_conversa(cliente):
    sessao = str(uuid.uuid4())
    cliente.post("/alexa", json=requisicao(sessao, "LaunchRequest"))
    falar(cliente, sessao, "meu filho")
    fim = cliente.post("/alexa", json=requisicao(sessao, "SessionEndedRequest", reason="USER_INITIATED"))
    assert fim.status_code == 200
    # Depois do fim, a mesma sessão começa do zero.
    assert "senha" in texto(falar(cliente, sessao, "foi o banco"))


def test_recusa_outra_skill(cliente):
    corpo = requisicao(str(uuid.uuid4()), "LaunchRequest")
    corpo["context"]["System"]["application"]["applicationId"] = "amzn1.ask.skill.outra"
    assert cliente.post("/alexa", json=corpo).status_code == 403


def test_recusa_requisicao_antiga(cliente):
    antigo = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    corpo = requisicao(str(uuid.uuid4()), "LaunchRequest", timestamp=antigo)
    assert cliente.post("/alexa", json=corpo).status_code == 400


def test_mascara_numeros_para_o_langfuse():
    dados = {"relato": ["pediu 400 reais", "o número é (11) 98765-4321"], "url": "https://x.gov.br/noticia/3823"}
    assert mascarar(data=dados) == {
        "relato": ["pediu [número] reais", "o número é [número]"],
        "url": "https://x.gov.br/noticia/3823",
    }


def test_mascara_a_fala_dentro_do_command_do_langgraph():
    from langgraph.types import Command

    mascarado = mascarar(data=Command(resume="ligar no 0800 123 4567"))
    assert "4567" not in str(mascarado)
    assert mascarado["resume"] == "ligar no [número]"
