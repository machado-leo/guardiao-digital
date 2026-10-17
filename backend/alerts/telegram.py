"""Alerta para a família pelo bot do Telegram.

O envio roda numa thread separada: a Alexa não pode esperar o Telegram responder.
A mensagem leva só o necessário para a família agir (nível de risco, golpe e
orientação dada); as falas do idoso, valores e nomes não saem daqui (LGPD).
"""

import logging
import os
import threading

import requests

from backend import config

log = logging.getLogger(__name__)

URL_API = "https://api.telegram.org/bot{token}/{metodo}"
TIMEOUT = 5


def montar_mensagem(risco: int, motivos: list[str], golpe: dict | None, fala: str) -> str:
    linhas = [
        "⚠️ Guardião Digital: possível golpe",
        "",
        f"Seu familiar acabou de consultar o Guardião e o risco ficou em {risco}/100.",
    ]
    if golpe:
        linhas.append(f"Parece o {golpe['nome']}.")
    if motivos:
        linhas.append(f"Sinais: {', '.join(motivos)}.")
    linhas += ["", f"O Guardião orientou: \"{fala}\"", "", "Ligue para seu familiar agora."]
    return "\n".join(linhas)


def _enviar(texto: str) -> bool:
    # O log diz só se falhou e por quê, nunca o texto do alerta.
    try:
        resposta = requests.post(
            URL_API.format(token=os.getenv("TELEGRAM_BOT_TOKEN"), metodo="sendMessage"),
            json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": texto},
            timeout=TIMEOUT,
        )
    except requests.RequestException as erro:
        log.warning("Alerta do Telegram não enviado: %s", type(erro).__name__)
        return False
    if not resposta.ok:
        log.warning("Alerta do Telegram recusado: HTTP %s", resposta.status_code)
    return resposta.ok


def enviar_alerta(texto: str) -> threading.Thread | None:
    """Dispara o envio em segundo plano. None quando o Telegram não está configurado."""
    if not config.telegram_configurado():
        return None
    envio = threading.Thread(target=_enviar, args=(texto,), name="alerta-telegram")
    envio.start()
    return envio
