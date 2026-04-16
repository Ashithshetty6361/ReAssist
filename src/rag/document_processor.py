"""
ReAssist — Document Processor
Upload -> chunk -> embed -> store in ChromaDB.
"""

import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from src.rag.embeddings import get_embeddings

CHROMA_DIR = "data/chromadb"


def process_upload(file_path: str, workspace_id: str, filename: str) -> dict:
    """
    Process an uploaded document into embedded chunks.

    Args:
        file_path: Path to the saved file on disk
        workspace_id: Workspace that owns this document
        filename: Original filename

    Returns:
        {"success": True, "chunks_stored": N, "collection": collection_name}
    """
    try:
        # Detect file type and load
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in (".txt", ".md"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            return {"success": False, "error": f"Unsupported file type: {ext}"}

        documents = loader.load()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(documents)

        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "workspace_id": workspace_id,
                "source": filename,
                "chunk_index": i,
            })

        # Embed and store in ChromaDB
        collection_name = f"ws_{workspace_id}"
        os.makedirs(CHROMA_DIR, exist_ok=True)

        Chroma.from_documents(
            documents=chunks,
            embedding=get_embeddings(),
            collection_name=collection_name,
            persist_directory=CHROMA_DIR,
        )

        return {
            "success": True,
            "chunks_stored": len(chunks),
            "collection": collection_name,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
