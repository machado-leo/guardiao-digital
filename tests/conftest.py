import pytest


@pytest.fixture(autouse=True)
def sem_servicos_externos(monkeypatch):
    """Testes rodam só com as regras: sem GPT, Langfuse ou Telegram, e com o limiar padrão."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    monkeypatch.setenv("RISK_ALERT_THRESHOLD", "70")
