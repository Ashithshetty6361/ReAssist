"""
Pipeline execution routes — Execute + List + Get
Powered by ResearchService and Service-Layer Abstraction.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from src.core.database import get_db, SessionLocal
from src.core.auth import get_current_user
from src.models.orm import (
    User, Workspace, PipelineExecution, WorkspaceStatus, ExecutionType
)
from src.api.schemas import QueryRequest
from src.api.serializers import (
    serialize_execution, serialize_trace
)
from src.services.research_service import get_research_service
from src.services.storage_service import get_storage_service
from src.core.config import DEFAULT_MODEL, MAX_PAPERS

router = APIRouter(tags=["pipeline"])


def _get_workspace_or_404(workspace_id: str, user_id: str, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


@router.post("/workspaces/{workspace_id}/execute")
def execute_pipeline(
    workspace_id: str,
    req: QueryRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)

    execution = PipelineExecution(
        workspace_id=ws.id,
        query=req.query,
        execution_type=ExecutionType(req.execution_type) if req.execution_type else ExecutionType.MULTI_AGENT,
        status="running"
    )
    db.add(execution)
    ws.status = WorkspaceStatus.SYNTHESIS
    ws.query = req.query
    ws.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(execution)

    exec_id = execution.id
    model = req.model or DEFAULT_MODEL
    max_papers = req.max_papers or MAX_PAPERS

    def run_pipeline():
        pdb = SessionLocal()
        try:
            research_service = get_research_service()
            research_service.run_pipeline_sync(
                workspace_id=ws.id,
                execution_id=exec_id,
                query=req.query,
                document_id=req.document_id,
                model=model,
                max_papers=max_papers,
                use_router=req.use_router,
                db=pdb,
            )
        except Exception as e:
            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "failed"
                ex.error = str(e)
                pdb.commit()
        finally:
            pdb.close()

    background_tasks.add_task(run_pipeline)
    return {"execution_id": exec_id, "status": "running"}


@router.get("/workspaces/{workspace_id}/executions")
def list_executions(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    execs = (
        db.query(PipelineExecution)
        .filter(PipelineExecution.workspace_id == ws.id)
        .order_by(PipelineExecution.created_at.desc())
        .all()
    )
    return [serialize_execution(e) for e in execs]


@router.get("/executions/{execution_id}")
def get_execution(
    execution_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")
    ws = db.query(Workspace).filter(Workspace.id == ex.workspace_id, Workspace.user_id == user.id).first()
    if not ws:
        raise HTTPException(403, "Access denied")

    storage = get_storage_service()
    result_data = None
    if ex.result_ref:
        try:
            raw_bytes = storage.retrieve_artifact(ex.result_ref)
            result_data = json.loads(raw_bytes.decode("utf-8"))
        except Exception:
            pass

    data = serialize_execution(ex)
    data["result"] = result_data
    data["traces"] = [serialize_trace(t) for t in ex.traces]
    return data
