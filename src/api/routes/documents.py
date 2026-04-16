"""
Document upload routes — RAG file uploads with vector embedding
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import hashlib
import os

from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.orm import User, Workspace, Document
from src.rag.document_processor import process_upload
from src.rag.retriever import retrieve_relevant_chunks

router = APIRouter(tags=["documents"])


class RAGQueryRequest(BaseModel):
    query: str
    k: Optional[int] = 10


def _get_workspace_or_404(workspace_id: str, user_id: str, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


@router.post("/workspaces/{workspace_id}/documents")
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Dedup check
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing and existing.workspace_id == ws.id:
        return {"message": "File already uploaded to this workspace", "document_id": existing.id}

    os.makedirs("data/uploads", exist_ok=True)
    blob_path = f"data/uploads/{file_hash}_{file.filename}"
    with open(blob_path, "wb") as f:
        f.write(content)

    # ── NEW: Chunk, embed, and store in ChromaDB ─────────────────────────
    rag_result = process_upload(blob_path, ws.id, file.filename)

    doc = Document(
        workspace_id=ws.id,
        filename=file.filename,
        file_hash=file_hash,
        blob_url=blob_path,
        vector_namespace=f"ws_{ws.id}"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "hash": file_hash,
        "rag": rag_result,
    }


@router.post("/workspaces/{workspace_id}/rag-query")
def rag_query(
    workspace_id: str,
    req: RAGQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Query the RAG vector store for a workspace's documents."""
    ws = _get_workspace_or_404(workspace_id, user.id, db)

    chunks = retrieve_relevant_chunks(ws.id, req.query, k=req.k)

    if not chunks:
        return {
            "success": False,
            "error": "No documents found. Upload documents first.",
            "chunks": [],
        }

    return {
        "success": True,
        "query": req.query,
        "chunks_found": len(chunks),
        "chunks": chunks,
    }
