"""Tradução entre o formato de requisição/resposta da Alexa e o Guardião."""

from datetime import datetime, timezone

# A Alexa reenvia requisições antigas em ataques de repetição; ela mesma recomenda 150 s.
TOLERANCIA_TIMESTAMP = 150

SIM_NAO = {"AMAZON.YesIntent": "sim", "AMAZON.NoIntent": "não"}
PARAR = {"AMAZON.StopIntent", "AMAZON.CancelIntent", "AMAZON.NavigateHomeIntent"}
AJUDA = "AMAZON.HelpIntent"
REPETIR = "AMAZON.RepeatIntent"

FALA_AJUDA = "Eu te ajudo a descobrir se uma mensagem ou ligação é golpe. Responda com calma. "
FALA_NAO_ENTENDI = "Desculpe, não entendi. "
FALA_REPROMPT = "Pode responder com calma. "
FALA_DESPEDIDA = "Tudo bem. Lembre: na dúvida, não pague nada antes de confirmar com alguém de confiança."


def id_da_skill(corpo: dict) -> str | None:
    sistema = corpo.get("context", {}).get("System", {})
    return (
        sistema.get("application", {}).get("applicationId")
        or corpo.get("session", {}).get("application", {}).get("applicationId")
    )


def timestamp_recente(corpo: dict, agora: datetime | None = None) -> bool:
    try:
        enviado = datetime.fromisoformat(corpo["request"]["timestamp"].replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return False
    agora = agora or datetime.now(timezone.utc)
    return abs((agora - enviado).total_seconds()) <= TOLERANCIA_TIMESTAMP


def texto_falado(intent: dict) -> str | None:
    """O que o idoso disse: sim/não dos intents prontos ou o primeiro slot preenchido."""
    if intent.get("name") in SIM_NAO:
        return SIM_NAO[intent["name"]]
    for slot in (intent.get("slots") or {}).values():
        if slot.get("value"):
            return slot["value"]
    return None


def resposta(fala: str, encerrar: bool, reprompt: str | None = None) -> dict:
    corpo = {"outputSpeech": {"type": "PlainText", "text": fala}, "shouldEndSession": encerrar}
    if reprompt and not encerrar:
        corpo["reprompt"] = {"outputSpeech": {"type": "PlainText", "text": reprompt}}
    return {"version": "1.0", "response": corpo}


def resposta_vazia() -> dict:
    return {"version": "1.0", "response": {}}
