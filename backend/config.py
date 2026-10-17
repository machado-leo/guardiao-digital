"""Configuração lida do .env, num lugar só."""

import os

from dotenv import load_dotenv

load_dotenv()


def limiar_alerta() -> int:
    """Risco (0 a 100) a partir do qual a família é avisada."""
    return int(os.getenv("RISK_ALERT_THRESHOLD", "70"))


def modelo_openai() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-6-luna")


def openai_configurado() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def telegram_configurado() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN")) and bool(os.getenv("TELEGRAM_CHAT_ID"))


def langfuse_ativo() -> bool:
    ligado = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
    return ligado and bool(os.getenv("LANGFUSE_PUBLIC_KEY")) and bool(os.getenv("LANGFUSE_SECRET_KEY"))
