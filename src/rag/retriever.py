"""
ReAssist — ChromaDB Retriever
Provides workspace-scoped vector retrieval for RAG queries.
"""

import os
from langchain_community.vectorstores import Chroma
from src.rag.embeddings import get_embeddings
from src.core.config import RAG_TOP_K

CHROMA_DIR = "data/chromadb"


def get_retriever(workspace_id: str, k: int = RAG_TOP_K):
    """
    Get a LangChain retriever for a specific workspace's document collection.

    Args:
        workspace_id: The workspace whose documents to search
        k: Number of chunks to retrieve (default from config)

    Returns:
        A LangChain retriever instance, or None if collection doesn't exist
    """
    collection_name = f"ws_{workspace_id}"

    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DIR,
        )
        return vectorstore.as_retriever(search_kwargs={"k": k})
    except Exception:
        return None


def retrieve_relevant_chunks(workspace_id: str, query: str, k: int = RAG_TOP_K) -> list[dict]:
    """
    Retrieve relevant document chunks for a query.

    Args:
        workspace_id: Workspace to search
        query: Search query
        k: Number of results

    Returns:
        List of {"content": str, "metadata": dict} dicts
    """
    retriever = get_retriever(workspace_id, k=k)
    if retriever is None:
        return []

    try:
        docs = retriever.invoke(query)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in docs
        ]
    except Exception:
        return []
