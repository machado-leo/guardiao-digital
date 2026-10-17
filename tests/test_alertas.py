from backend.alerts import telegram
from backend.graph import grafo

GOLPE = {"id": "falso-parente-numero-novo", "nome": "golpe do falso parente", "acao": "...", "fonte": "f", "url": "u"}


def test_mensagem_tem_o_que_a_familia_precisa():
    texto = telegram.montar_mensagem(90, ["número novo", "pediram PIX ou pagamento"], GOLPE, "Não faça o PIX.")
    assert "90/100" in texto
    assert "golpe do falso parente" in texto
    assert "número novo, pediram PIX ou pagamento" in texto
    assert '"Não faça o PIX."' in texto
    assert "Ligue para seu familiar agora." in texto


def test_sem_telegram_configurado_nao_envia():
    assert telegram.enviar_alerta("teste") is None


def test_avisar_familia_nao_manda_as_falas_do_idoso(monkeypatch):
    enviados = []
    monkeypatch.setattr(grafo, "enviar_alerta", lambda texto: enviados.append(texto) or object())

    estado = {
        "risco": 100,
        "motivos": ["número novo"],
        "golpe": GOLPE,
        "veredito": "Não faça o PIX.",
        "relato": ["Meu filho Pedro", "Pediu 400 reais no PIX para a conta da Maria"],
    }
    assert grafo.avisar_familia(estado) == {"alerta_enviado": True}
    assert len(enviados) == 1
    for trecho in ("Pedro", "400", "Maria"):
        assert trecho not in enviados[0]
