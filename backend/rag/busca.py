"""Índice da base de golpes no ChromaDB e busca do caso mais parecido com a conversa.

A busca combina filtros e similaridade: primeiro restringe aos casos com o mesmo
pedido (e o mesmo remetente, quando ele é conhecido) e só então compara os textos.
Assim um pedido de código nunca recebe a orientação de um golpe de PIX.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from backend import config
from backend.rag.base import Golpe, carregar, por_id

if TYPE_CHECKING:
    # Só para anotação: importar de verdade criaria um ciclo com o grafo, que usa esta busca.
    from backend.graph.estado import Estado

PASTA_INDICE = Path(__file__).resolve().parents[2] / "data" / "index"
COLECAO = "golpes"
MODELO_EMBEDDING = "text-embedding-3-small"

# Distância de cosseno acima da qual o caso é considerado diferente demais.
# Calibrada com conversas de teste: acertos ficaram até ~0,45 e casos sem relação acima de 0,6.
DISTANCIA_MAXIMA = 0.55
CANDIDATOS = 3

PEDIDOS = ["senha", "codigo", "pix", "link", "dados", "ligar"]

REMETENTE_TEXTO = {
    "familia": "um parente",
    "banco": "o banco",
    "inss": "o INSS",
    "loja": "uma loja ou os Correios",
    "outro": "alguém desconhecido",
}

PEDIDO_TEXTO = {
    "senha": "a senha",
    "codigo": "o código que chegou por SMS",
    "pix": "um PIX ou pagamento",
    "link": "clicar num link ou instalar um aplicativo",
    "dados": "dados pessoais ou documentos",
    "ligar": "ligar para outro número",
    "nada": "nada",
    "outro": "outra coisa",
}


@lru_cache(maxsize=1)
def _cliente():
    import chromadb

    return chromadb.PersistentClient(
        path=str(PASTA_INDICE), settings=chromadb.Settings(anonymized_telemetry=False)
    )


def _funcao_embedding():
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

    return OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"), model_name=MODELO_EMBEDDING)


@lru_cache(maxsize=1)
def _colecao():
    return _cliente().get_or_create_collection(
        COLECAO, embedding_function=_funcao_embedding(), configuration={"hnsw": {"space": "cosine"}}
    )


def indexar(golpes: list[Golpe] | None = None) -> int:
    """Recria o índice a partir da base. Devolve quantos casos foram indexados."""
    golpes = golpes if golpes is not None else carregar()
    cliente = _cliente()
    if COLECAO in [c.name for c in cliente.list_collections()]:
        cliente.delete_collection(COLECAO)
    _colecao.cache_clear()

    _colecao().add(
        ids=[g.id for g in golpes],
        documents=[g.texto_para_busca() for g in golpes],
        metadatas=[
            {"remetente": g.remetente, **{f"pede_{p}": p in g.pedidos for p in PEDIDOS}} for g in golpes
        ],
    )
    return len(golpes)


def descrever(estado: Estado) -> str:
    """Resume a conversa num texto comparável com os casos da base.

    O relato do idoso vem primeiro: é ele que diferencia, por exemplo, o falso
    sequestro do falso parente, que têm o mesmo remetente e o mesmo pedido.
    """
    resumo = [f"Contato de {REMETENTE_TEXTO.get(estado.get('remetente', 'outro'))}"]
    if estado.get("numero_novo") is True:
        resumo.append("usando um número novo")
    elif estado.get("numero_novo") is False:
        resumo.append("usando o número de sempre")
    resumo.append(f"pedindo {PEDIDO_TEXTO.get(estado.get('pedido', 'outro'))}")
    if estado.get("urgencia"):
        resumo.append("com urgência ou ameaça")

    relato = " ".join(estado.get("relato", []))
    return f"{relato}. {', '.join(resumo)}." if relato else f"{', '.join(resumo)}."


def _combina(golpe: Golpe, estado: Estado) -> bool:
    return golpe.numero_novo is None or golpe.numero_novo == estado.get("numero_novo")


def _filtros(estado: Estado) -> list[dict | None]:
    """Filtros do mais específico ao mais amplo."""
    remetente = estado.get("remetente", "outro")
    pedido = estado.get("pedido")
    por_remetente = {"remetente": remetente} if remetente != "outro" else None
    por_pedido = {f"pede_{pedido}": True} if pedido in PEDIDOS else None

    if por_remetente and por_pedido:
        return [{"$and": [por_remetente, por_pedido]}, por_pedido]
    return [por_remetente or por_pedido]


def buscar(estado: Estado) -> tuple[Golpe, float] | None:
    """Caso da base mais parecido com a conversa, com a distância. None se nada servir."""
    if not config.openai_configurado():
        return None
    colecao = _colecao()
    if colecao.count() == 0:
        indexar()
        colecao = _colecao()

    texto = descrever(estado)
    for filtro in _filtros(estado):
        resultado = colecao.query(query_texts=[texto], n_results=CANDIDATOS, where=filtro)
        for golpe_id, distancia in zip(resultado["ids"][0], resultado["distances"][0]):
            golpe = por_id()[golpe_id]
            if distancia <= DISTANCIA_MAXIMA and _combina(golpe, estado):
                return golpe, distancia
    return None
