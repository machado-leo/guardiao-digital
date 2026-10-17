"""Mostra o ID dos chats que mandaram mensagem para o bot, para preencher TELEGRAM_CHAT_ID.

    1. No Telegram, mande /start para o bot (ou adicione o bot num grupo da família).
    2. python -m backend.alerts.descobrir_chat
"""

import os

import requests

from backend import config  # noqa: F401  (carrega o .env)
from backend.alerts.telegram import URL_API, TIMEOUT


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Preencha TELEGRAM_BOT_TOKEN no .env.")
    resposta = requests.get(URL_API.format(token=token, metodo="getUpdates"), timeout=TIMEOUT).json()

    chats = {}
    for update in resposta.get("result", []):
        mensagem = update.get("message") or update.get("my_chat_member") or {}
        if "chat" in mensagem:
            chat = mensagem["chat"]
            chats[chat["id"]] = chat.get("title") or chat.get("first_name") or chat.get("type")

    if not chats:
        raise SystemExit("Nenhum chat ainda. Mande /start para o bot no Telegram e rode de novo.")
    for chat_id, nome in chats.items():
        print(f"TELEGRAM_CHAT_ID={chat_id}   ({nome})")


if __name__ == "__main__":
    main()
