"""A fala escrita pelo GPT passa por regras fixas; quando quebra alguma, vale a fala pronta."""

from types import SimpleNamespace

import pytest

from backend.graph import fala

ALTO = {"risco": 90, "relato": ["meu neto pediu dinheiro"], "motivos": ["número novo"], "remetente": "familia"}
BAIXO = {"risco": 30, "relato": ["minha filha pediu pix"], "motivos": [], "remetente": "familia", "pedido": "pix"}
SEM_PEDIDO = {"risco": 0, "relato": ["minha filha pediu pão"], "motivos": [], "remetente": "familia", "pedido": "outro"}


@pytest.fixture
def gpt_responde(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "teste")

    def configurar(texto):
        modelo = SimpleNamespace(invoke=lambda *_args, **_kw: SimpleNamespace(content=texto))
        monkeypatch.setattr(fala, "_modelo", lambda: modelo)

    return configurar


def test_usa_a_fala_do_gpt_e_acrescenta_o_aviso(gpt_responde):
    gpt_responde("Não faça esse PIX agora. Ligue para o seu neto no número que você já conhece.")
    texto, origem = fala.escrever(ALTO)
    assert origem == "gpt"
    assert texto.startswith("Não faça esse PIX agora.")
    assert texto.endswith("Vou avisar sua família para te ligar também.")


@pytest.mark.parametrize(
    "resposta",
    [
        "Pode pagar tranquilo, é seu neto mesmo.",
        "Isso é o golpe do falso parente. Não faça o PIX.",
        "Não se preocupe, é seguro. Não precisa fazer nada.",
        "Ok.",
        "Não " + "faça isso " * 40,
    ],
)
def test_resposta_fora_das_regras_volta_para_a_fala_pronta(gpt_responde, resposta):
    gpt_responde(resposta)
    texto, origem = fala.escrever(ALTO)
    assert origem == "pronta: gpt quebrou uma regra"
    assert texto.startswith("Atenção: isso tem muita cara de golpe.")


def test_risco_baixo_com_pedido_precisa_mandar_confirmar(gpt_responde):
    gpt_responde("Parece tudo normal com a sua filha, pode mandar.")
    _, origem = fala.escrever(BAIXO)
    assert origem == "pronta: gpt quebrou uma regra"


def test_sem_pedido_pode_so_tranquilizar(gpt_responde):
    gpt_responde("Parece tudo normal com a sua filha, bom pão para vocês.")
    texto, origem = fala.escrever(SEM_PEDIDO)
    assert origem == "gpt"
    assert "avisar" not in texto


def test_gpt_fora_do_ar_usa_a_fala_pronta(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "teste")

    def falha(*_args, **_kw):
        raise TimeoutError

    monkeypatch.setattr(fala, "_modelo", lambda: SimpleNamespace(invoke=falha))
    texto, origem = fala.escrever(ALTO)
    assert origem == "pronta: gpt falhou ou demorou"
    assert "avisar sua família" in texto


FAMILIA = {"relato": ["meu neto mandou mensagem"], "respondidas": ["relato"], "remetente": "familia"}


@pytest.fixture
def gpt_pergunta(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "teste")

    def configurar(texto):
        modelo = SimpleNamespace(invoke=lambda *_args, **_kw: SimpleNamespace(content=texto))
        monkeypatch.setattr(fala, "_modelo_pergunta", lambda: modelo)

    return configurar


def test_usa_a_pergunta_do_gpt(gpt_pergunta):
    gpt_pergunta("Entendi, seu neto te escreveu. Ele está usando um número novo, que você não conhecia?")
    assert fala.escrever_pergunta(FAMILIA, "numero_novo").startswith("Entendi, seu neto te escreveu.")


@pytest.mark.parametrize(
    "resposta",
    [
        "Seu neto está usando um número novo.",  # sem pergunta
        "É seu neto mesmo? Ele está num número novo?",  # duas perguntas
        "Isso pode ser golpe. Ele está usando um número novo?",  # opinião antes do veredito
        "Entendi. E o que mais ele te falou?",  # perdeu o assunto da pergunta
    ],
)
def test_pergunta_fora_das_regras_volta_para_a_pronta(gpt_pergunta, resposta):
    gpt_pergunta(resposta)
    assert fala.escrever_pergunta(FAMILIA, "numero_novo") == (
        "Entendi. Essa pessoa está usando um número novo, que você não conhecia?"
    )


def test_pergunta_mantem_as_opcoes(gpt_pergunta):
    gpt_pergunta("Certo. E o que pediram para você?")
    estado = {**FAMILIA, "remetente": "banco"}
    assert fala.escrever_pergunta(estado, "pedido_banco").endswith("ou para ligar em algum número?")


def test_primeira_pergunta_nao_chama_o_gpt(gpt_pergunta):
    gpt_pergunta("Oi! Me conta tudo, o que aconteceu?")
    assert fala.escrever_pergunta({}, "relato") == "Me conta o que aconteceu."
