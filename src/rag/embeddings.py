"""
ReAssist — Embedding singleton
Provides OpenAI embeddings for the RAG pipeline.
"""

import os
from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from src.core.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of text strings into vectors."""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)
