"""
Document upload routes — RAG file uploads with vector embedding
Powered by StorageService and RAGService.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.orm import User, Workspace, Document
from src.services.storage_service import get_storage_service
from src.services.rag_service import get_rag_service

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
    storage_service = get_storage_service()
    rag_service = get_rag_service()

    content = await file.read()
    file_hash = storage_service.calculate_sha256(content)

    # Dedup check
    existing = db.query(Document).filter(Document.file_hash == file_hash, Document.workspace_id == ws.id).first()
    if existing:
        return {"message": "File already uploaded to this workspace", "document_id": existing.id}

    # Store file via storage service (Local disk or S3)
    stored = storage_service.store_document(content=content, filename=file.filename, workspace_id=ws.id)

    # Chunk, embed, and store in ChromaDB
    rag_result = rag_service.ingest_document(
        file_path=stored["blob_url"],
        workspace_id=ws.id,
        filename=file.filename
    )

    doc = Document(
        workspace_id=ws.id,
        filename=file.filename,
        file_hash=file_hash,
        blob_url=stored["blob_url"],
        vector_namespace=f"ws_{ws.id}"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "hash": file_hash,
        "accessible_url": stored["accessible_url"],
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
    rag_service = get_rag_service()

    chunks = rag_service.retrieve_context(ws.id, req.query, k=req.k or 10)

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
