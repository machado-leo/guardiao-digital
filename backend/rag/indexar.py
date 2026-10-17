"""Recria o índice vetorial a partir de data/golpes/golpes.json.

    python -m backend.rag.indexar

Rode de novo sempre que editar a base de golpes.
"""

from backend import config
from backend.rag.busca import PASTA_INDICE, indexar


def main() -> None:
    if not config.openai_configurado():
        raise SystemExit("Preencha OPENAI_API_KEY no .env: os embeddings usam a API da OpenAI.")
    total = indexar()
    print(f"{total} golpes indexados em {PASTA_INDICE}")


if __name__ == "__main__":
    main()
