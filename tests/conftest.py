import pytest


@pytest.fixture(autouse=True)
def sem_servicos_externos(monkeypatch):
    """Testes rodam só com as regras: sem GPT, sem Langfuse e com o limiar padrão."""
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    monkeypatch.setenv("RISK_ALERT_THRESHOLD", "70")
