"""
Export routes — Export Research Intelligence Dossiers in Markdown, JSON, and BibTeX format
"""

import json
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.orm import User, PipelineExecution, Workspace
from src.services.export_service import get_export_service
from src.services.storage_service import get_storage_service

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/executions/{execution_id}")
def export_execution_dossier(
    execution_id: str,
    format: str = Query("markdown", regex="^(markdown|json|bibtex)$"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a completed research pipeline execution as a publication-ready Markdown dossier,
    structured JSON, or BibTeX bibliography.
    """
    ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")

    ws = db.query(Workspace).filter(Workspace.id == ex.workspace_id, Workspace.user_id == user.id).first()
    if not ws:
        raise HTTPException(403, "Access denied")

    if not ex.result_ref:
        raise HTTPException(400, "Execution has no result artifact to export")

    storage = get_storage_service()
    try:
        raw_bytes = storage.retrieve_artifact(ex.result_ref)
        result_data = json.loads(raw_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(500, f"Could not load execution artifact: {e}")

    export_service = get_export_service()
    exported = export_service.export_dossier(
        execution_id=execution_id,
        query=ex.query,
        execution_result=result_data,
        format=format
    )

    return exported
