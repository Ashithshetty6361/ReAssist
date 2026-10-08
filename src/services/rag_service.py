"""
ReAssist — RAG Service Layer
Encapsulates workspace-scoped vector indexing, chunking, and semantic retrieval with ChromaDB.
"""

from typing import List, Dict, Any, Optional
from src.rag.document_processor import process_upload
from src.rag.retriever import retrieve_relevant_chunks, get_retriever
from src.core.config import RAG_TOP_K


class RAGService:
    """Service managing workspace document embeddings, vector indexing, and retrieval."""

    def ingest_document(self, file_path: str, workspace_id: str, filename: str) -> dict:
        """Process, chunk, embed, and store document in ChromaDB."""
        return process_upload(file_path=file_path, workspace_id=workspace_id, filename=filename)

    def retrieve_context(self, workspace_id: str, query: str, k: int = RAG_TOP_K) -> List[Dict[str, Any]]:
        """Retrieve relevant context chunks for a workspace query."""
        return retrieve_relevant_chunks(workspace_id=workspace_id, query=query, k=k)

    def search_with_scores(self, workspace_id: str, query: str, k: int = RAG_TOP_K, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks and filter by minimum similarity score."""
        chunks = self.retrieve_context(workspace_id=workspace_id, query=query, k=k)
        # Filter if relevance_score is present in metadata
        filtered = []
        for chunk in chunks:
            score = chunk.get("metadata", {}).get("relevance_score", 1.0)
            if score >= min_score:
                filtered.append(chunk)
        return filtered or chunks


_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
