"""Conversas completas por texto, do jeito que o idoso falaria."""

import uuid

import pytest

from backend.graph import Guardiao


def conversar(*respostas: str):
    guardiao = Guardiao()
    sessao_id = str(uuid.uuid4())
    turno = guardiao.iniciar(sessao_id)
    for resposta in respostas:
        assert not turno.encerrou, "a conversa terminou antes do esperado"
        turno = guardiao.responder(sessao_id, resposta)
    assert turno.encerrou, "a conversa ainda tem perguntas"
    return turno


@pytest.mark.parametrize(
    ("respostas", "alertar"),
    [
        (["Meu filho", "Tá, disse que o celular caiu na água", "Que perdeu o celular",
          "Pediu 400 reais no PIX", "Disse que era urgente"], True),
        (["O banco", "Pediram o código que chegou por SMS", "Não"], True),
        (["Foi o INSS", "Sim, um link pra prova de vida", "Falaram que ia cortar o benefício"], True),
        (["Uma loja, dos correios", "Pagar uma taxa de frete", "Falaram que ia devolver hoje"], True),
        (["Minha neta", "Não, é o mesmo número", "Não pediu nada, só mandou foto", "Não"], False),
    ],
)
def test_conversa(respostas, alertar):
    turno = conversar(*respostas)
    assert turno.alertar is alertar


def test_falso_parente_manda_nao_fazer_o_pix():
    turno = conversar("Meu neto", "Sim", "Trocou de celular", "Mil reais", "Não")
    assert "Não faça o PIX" in turno.fala
    assert "avisar sua família" in turno.fala


def test_parente_pedindo_codigo_fala_de_codigo_e_nao_de_pix():
    turno = conversar("Minha filha", "Não, é o número de sempre", "Pediu o código que chegou", "Não")
    assert "código" in turno.fala
    assert "PIX" not in turno.fala


def test_desculpa_so_e_perguntada_com_numero_novo():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    guardiao.responder("s", "Meu filho")
    turno = guardiao.responder("s", "Não, o mesmo número")
    assert turno.pergunta_id == "pedido_familia"


def test_nunca_autoriza_pagamento():
    turno = conversar("Minha neta", "Não, é o mesmo número", "Nada", "Não")
    assert "pode pagar" not in turno.fala.lower()
    assert "confirme antes" in turno.fala.lower()


def test_falso_sequestro_avisa_a_familia():
    turno = conversar(
        "Meu neto",
        "Não sei, era uma ligação, uma voz chorando",
        "Pediram dinheiro de resgate, senão iam machucar ele",
        "Sim, disseram pra eu não desligar",
    )
    assert turno.alertar is True
    assert "Mantenha a calma" in turno.fala


def test_sequestro_pula_a_pergunta_do_numero_novo():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder("s", "Ligaram dizendo que sequestraram meu neto")
    assert turno.pergunta_id == "pedido_familia"


def test_relato_completo_vai_direto_ao_veredito():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder(
        "s", "Meu neto mandou mensagem de um número novo pedindo 500 reais no pix, disse que era urgente"
    )
    assert turno.encerrou
    assert turno.alertar is True


def test_relato_so_pergunta_o_que_faltou():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder("s", "O banco me mandou uma mensagem pedindo a senha")
    assert turno.pergunta_id == "urgencia"
    assert turno.fala.startswith("Entendi.")


def test_relato_sem_remetente_pergunta_quem_foi():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder("s", "volume cinco")
    assert turno.pergunta_id == "remetente"


def test_ligaram_nao_e_pedido_de_ligar():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder("s", "Ligaram do banco")
    assert turno.pergunta_id == "pedido_banco"


def test_um_transcrito_como_1_nao_vira_pix():
    guardiao = Guardiao()
    guardiao.iniciar("s")
    turno = guardiao.responder("s", "1 carta aqui em casa")
    assert turno.pergunta_id == "remetente"


def test_valor_com_reais_no_relato_vira_pix():
    from backend.graph.interpretar import interpretar

    campos = interpretar("relato", "meu neto pediu 300 reais")
    assert campos["pedido"] == "pix"
    assert campos["valor"] == 300
