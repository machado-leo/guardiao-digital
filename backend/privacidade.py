"""Máscara de dados pessoais antes de qualquer coisa sair para o Langfuse (LGPD).

Troca sequências de números (telefone, CPF, valores, códigos) por "[número]".
Nomes ditos pelo idoso não são detectáveis com segurança por regra; por isso
a observabilidade deve ser testada com dados fictícios.
"""

import dataclasses
import re

NUMEROS = re.compile(r"\(?\d[\d\s.,()/-]*\d|\d")


def mascarar_texto(texto: str) -> str:
    # Links das fontes da base de golpes não são dado pessoal e ficam como estão.
    if texto.startswith(("http://", "https://")):
        return texto
    return NUMEROS.sub("[número]", texto)


def mascarar(data=None, **_):
    """Assinatura esperada pelo parâmetro mask do cliente do Langfuse."""
    if isinstance(data, str):
        return mascarar_texto(data)
    if isinstance(data, dict):
        return {chave: mascarar(valor) for chave, valor in data.items()}
    if isinstance(data, (list, tuple)):
        return type(data)(mascarar(item) for item in data)
    # Objetos como o Command(resume=...) do LangGraph chegam inteiros e seriam
    # serializados depois, sem passar pela máscara.
    if dataclasses.is_dataclass(data) and not isinstance(data, type):
        return mascarar(dataclasses.asdict(data))
    if hasattr(data, "model_dump"):
        return mascarar(data.model_dump())
    return data
