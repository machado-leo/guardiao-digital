"""A base é escrita à mão: estes testes pegam erro de digitação antes da demo."""

from backend.graph.grafo import consultar_base
from backend.graph.veredito import redigir_veredito
from backend.rag.base import carregar
from backend.rag.busca import PEDIDOS

REMETENTES = {"familia", "banco", "inss", "loja", "outro"}
GOLPES = carregar()


def test_tamanho_da_base():
    assert 20 <= len(GOLPES) <= 30


def test_ids_unicos():
    ids = [g.id for g in GOLPES]
    assert len(ids) == len(set(ids))


def test_campos_validos():
    for golpe in GOLPES:
        assert golpe.remetente in REMETENTES, golpe.id
        assert golpe.pedidos and set(golpe.pedidos) <= set(PEDIDOS), golpe.id
        assert golpe.nome.startswith("golpe "), golpe.id
        assert golpe.sinais, golpe.id
        assert golpe.fonte.url.startswith("https://"), golpe.id


def test_acao_curta_e_segura():
    for golpe in GOLPES:
        assert "pode pagar" not in golpe.acao.lower(), golpe.id
        assert len(golpe.acao) <= 160, f"{golpe.id}: fala longa demais para a Alexa"


def test_todo_remetente_tem_casos():
    assert {g.remetente for g in GOLPES} == REMETENTES


GOLPE = {"id": "x", "nome": "golpe do teste", "acao": "Não faça o PIX.", "fonte": "f", "url": "u", "distancia": 0.3}


def test_veredito_alto_fala_da_gravidade_e_da_acao_do_caso():
    fala = redigir_veredito({"risco": 90, "golpe": GOLPE})
    assert fala.startswith("Atenção: isso tem muita cara de golpe. Não faça o PIX.")
    assert "avisar sua família" in fala
    assert "golpe do teste" not in fala


def test_veredito_medio_usa_a_acao_do_caso_sem_alerta():
    fala = redigir_veredito({"risco": 50, "golpe": GOLPE})
    assert fala == "Cuidado: isso tem sinais de golpe. Não faça o PIX."


def test_sem_pedido_suspeito_nao_consulta_a_base():
    assert consultar_base({"pedido": "nada"}) == {"golpe": None}
    assert consultar_base({"pedido": "outro"}) == {"golpe": None}
