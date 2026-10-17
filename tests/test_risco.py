import pytest

from backend.graph.risco import avaliar_risco, nivel


@pytest.mark.parametrize(
    ("estado", "esperado"),
    [
        # Falso parente
        ({"remetente": "familia", "numero_novo": True, "pedido": "pix", "urgencia": True}, "alto"),
        ({"remetente": "familia", "numero_novo": True, "pedido": "pix", "urgencia": False}, "alto"),
        # Clonagem de WhatsApp: "parente" pede o código que chegou por SMS
        ({"remetente": "familia", "numero_novo": False, "pedido": "codigo", "urgencia": False}, "alto"),
        # Falsa central bancária
        ({"remetente": "banco", "pedido": "senha", "urgencia": False}, "alto"),
        ({"remetente": "banco", "pedido": "ligar", "urgencia": True}, "alto"),
        ({"remetente": "banco", "pedido": "ligar", "urgencia": False}, "medio"),
        # Falso INSS
        ({"remetente": "inss", "pedido": "link", "urgencia": True}, "alto"),
        ({"remetente": "inss", "pedido": "link", "urgencia": False}, "medio"),
        # Falso frete
        ({"remetente": "loja", "pedido": "pix", "urgencia": True}, "alto"),
        ({"remetente": "loja", "pedido": "pix", "urgencia": False}, "medio"),
        # WhatsApp clonado: parente pede dinheiro do número de sempre
        ({"remetente": "familia", "numero_novo": False, "pedido": "pix", "urgencia": False}, "medio"),
        # Desconhecido
        ({"remetente": "outro", "pedido": "link", "urgencia": False}, "medio"),
        # Sem sinais fortes
        ({"remetente": "familia", "numero_novo": False, "pedido": "nada", "urgencia": False}, "baixo"),
        ({"remetente": "inss", "pedido": "nada", "urgencia": None}, "baixo"),
    ],
)
def test_nivel_de_risco(estado, esperado):
    risco, _ = avaliar_risco(estado)
    assert nivel(risco) == esperado


def test_risco_nunca_passa_de_100():
    risco, _ = avaliar_risco({"remetente": "banco", "pedido": "senha", "numero_novo": True, "urgencia": True})
    assert risco == 100


def test_motivos_explicam_a_nota():
    risco, motivos = avaliar_risco({"remetente": "familia", "numero_novo": True, "pedido": "pix"})
    assert risco == 90
    assert motivos == [
        "pediram PIX ou pagamento",
        "número novo",
        "parente pedindo dinheiro por mensagem",
        "padrão do golpe do falso parente",
    ]


def test_limiar_vem_do_env(monkeypatch):
    monkeypatch.setenv("RISK_ALERT_THRESHOLD", "90")
    assert nivel(80) == "medio"


def test_parecer_com_golpe_conhecido_pode_tornar_critico():
    estado = {"remetente": "inss", "pedido": "link", "urgencia": False}
    sem_base, _ = avaliar_risco(estado)
    com_base, motivos = avaliar_risco({**estado, "golpe": {"id": "inss-prova-de-vida-link"}})
    assert nivel(sem_base) == "medio"
    assert nivel(com_base) == "alto"
    assert "parecido com um golpe conhecido da base" in motivos
