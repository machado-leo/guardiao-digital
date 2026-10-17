"""Estado da conversa: cada resposta do idoso preenche um campo."""

from typing import Literal, TypedDict

Remetente = Literal["familia", "banco", "inss", "loja", "outro"]
Pedido = Literal["senha", "codigo", "pix", "link", "dados", "ligar", "nada", "outro"]


class Estado(TypedDict, total=False):
    remetente: Remetente
    numero_novo: bool | None
    desculpa: str
    pedido: Pedido
    valor: int | None
    urgencia: bool | None
    sequestro: bool  # alguém falou em sequestro ou resgate
    relato: list[str]  # respostas como o idoso falou, usadas na busca da base de golpes

    # Controle do fluxo
    respondidas: list[str]  # ids das perguntas já feitas
    proxima: str | None  # próxima pergunta; None quando já dá para decidir

    # Resultado
    risco: int
    motivos: list[str]
    alertar: bool
    golpe: dict | None  # caso mais parecido da base: id, nome, acao, fonte, url, distancia
    veredito: str
    alerta_enviado: bool  # alerta disparado no Telegram (o envio termina em segundo plano)
