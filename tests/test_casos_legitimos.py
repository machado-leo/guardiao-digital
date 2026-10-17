"""Situações normais do dia a dia: o Guardião não pode avisar a família por elas.

Cada caso tem o relato e as respostas para as perguntas que o Guardião fizer, já que
as perguntas mudam conforme o que o relato contou.
"""

import uuid

import pytest

from backend.graph import Guardiao

CASOS = [
    ("minha filha pediu para eu comprar pão", {"numero_novo": "não, o número de sempre", "pedido_familia": "comprar pão na padaria", "urgencia": "não"}, "baixo"),
    ("o banco mandou mensagem avisando que a fatura fechou", {"pedido_banco": "não pediu nada, só avisou", "urgencia": "não"}, "baixo"),
    ("meu neto ligou para saber como eu estou", {"numero_novo": "não, é o número dele de sempre", "pedido_familia": "não pediu nada", "urgencia": "não"}, "baixo"),
    ("a farmácia avisou que meu remédio chegou", {"remetente": "uma loja", "pedido_geral": "não pediu nada, só avisou", "urgencia": "não"}, "baixo"),
    ("o inss mandou uma carta dizendo que meu benefício foi reajustado", {"link_inss": "não, não mandaram link nenhum", "urgencia": "não"}, "baixo"),
    ("os correios deixaram um aviso de entrega", {"pedido_geral": "nada, só buscar na agência", "urgencia": "não"}, "baixo"),
    ("minha vizinha pediu para eu regar as plantas", {"remetente": "uma vizinha", "pedido_geral": "regar as plantas", "urgencia": "não"}, "baixo"),
    ("a loja confirmou minha compra pelo aplicativo", {"pedido_geral": "não pediu nada", "urgencia": "não"}, "baixo"),
    ("uma carta chegou em casa", {"remetente": "da prefeitura", "pedido_geral": "não pediu nada", "urgencia": "não"}, "baixo"),
    # Parente pedindo dinheiro do número de sempre: a Febraban manda confirmar, mas não é alarme.
    ("meu filho pediu 50 reais emprestado do número de sempre", {"urgencia": "não"}, "medio"),
]


def conversar(relato: str, respostas: dict[str, str]):
    guardiao = Guardiao()
    sessao = str(uuid.uuid4())
    guardiao.iniciar(sessao)
    turno = guardiao.responder(sessao, relato)
    while not turno.encerrou:
        assert turno.pergunta_id in respostas, f"pergunta inesperada: {turno.pergunta_id}"
        turno = guardiao.responder(sessao, respostas[turno.pergunta_id])
    return turno


@pytest.mark.parametrize(("relato", "respostas", "esperado"), CASOS, ids=[c[0] for c in CASOS])
def test_caso_legitimo_nao_vira_alerta(relato, respostas, esperado):
    from backend.graph.risco import nivel

    turno = conversar(relato, respostas)
    assert turno.alertar is False
    assert nivel(turno.risco) == esperado, f"risco {turno.risco}: {turno.motivos}"
    assert "pode pagar" not in turno.fala.lower()
