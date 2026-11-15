"""
ReAssist — Pipeline Execution API Routes
=========================================
File: src/api/routes/pipeline.py

ARCHITECTURAL PURPOSE:
  This module exposes the REST API interface for triggering and monitoring research pipelines.
  It acts as the decoupling bridge between the synchronous HTTP client (Next.js frontend)
  and the asynchronous, long-running LangGraph multi-agent execution engine.

KEY DESIGN DECISIONS TO EXPLAIN IN INTERVIEWS / DEFENSE:
  1. Asynchronous Job Queue (FastAPI BackgroundTasks):
     - Running 11 agents takes ~25-35s (cloud) or longer on local models.
     - Keeping an HTTP connection open would cause browser timeouts and proxy drops.
     - By using BackgroundTasks, the endpoint creates a DB execution record and returns
       HTTP 200 with an execution_id in < 15ms. The UI then polls for progress.
  2. Multi-Tenant Workspace Scoping:
     - All executions are strictly scoped to `workspace_id` and verified against `user.id`.
  3. Session-per-Thread Safety:
     - The background task instantiates its own isolated database session (`SessionLocal`),
       preventing database session contention with the main request handler.
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


# ─────────────────────────────────────────────────────────────────────────────
# 1. SECURITY & ACCESS CONTROL HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _get_workspace_or_404(workspace_id: str, user_id: str, db: Session) -> Workspace:
    """
    Ensures multi-tenant workspace isolation.
    Guarantees that a user can only access pipelines belonging to their own workspaces.
    """
    ws = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


# ─────────────────────────────────────────────────────────────────────────────
# 2. DISPATCH ENDPOINT — POST /workspaces/{id}/execute
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/workspaces/{workspace_id}/execute")
def execute_pipeline(
    workspace_id: str,
    req: QueryRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dispatches a research pipeline asynchronously.
    
    WALKTHROUGH FLOW:
      Step 1: Verify workspace ownership.
      Step 2: Create a 'running' PipelineExecution record in SQLite/PostgreSQL.
      Step 3: Enqueue `run_pipeline` into FastAPI BackgroundTasks worker pool.
      Step 4: Return execution_id immediately (< 15ms) for client polling.
    """
    # Step 1: Validate tenant authorization
    ws = _get_workspace_or_404(workspace_id, user.id, db)

    # Step 2: Initialize execution record in the database
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

    # Step 3: Background Worker Function (Runs detached from HTTP socket)
    def run_pipeline():
        # Open an independent database session for the background worker thread
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
            # Graceful error handling: ensure execution is marked 'failed' in DB if crashes occur
            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "failed"
                ex.error = str(e)
                pdb.commit()
        finally:
            pdb.close()

    # Step 4: Dispatch to non-blocking background queue
    background_tasks.add_task(run_pipeline)
    return {"execution_id": exec_id, "status": "running"}


# ─────────────────────────────────────────────────────────────────────────────
# 3. LIST EXECUTIONS — GET /workspaces/{id}/executions
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/workspaces/{workspace_id}/executions")
def list_executions(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists past research runs for the workspace, ordered by newest first.
    Used by the sidebar and history explorer in the Next.js UI.
    """
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    execs = (
        db.query(PipelineExecution)
        .filter(PipelineExecution.workspace_id == ws.id)
        .order_by(PipelineExecution.created_at.desc())
        .all()
    )
    return [serialize_execution(e) for e in execs]


# ─────────────────────────────────────────────────────────────────────────────
# 4. POLL / GET SINGLE EXECUTION — GET /executions/{id}
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/executions/{execution_id}")
def get_execution(
    execution_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Polling endpoint used by the frontend to monitor progress and fetch final dossiers.
    
    RETURNS:
      - Execution metadata: status ('running' | 'completed' | 'failed'), latency, timestamps
      - Result dossier: synthesized papers, gaps, hypotheses, verification score
      - Agent traces: per-agent token counts and execution times for telemetry dashboards
    """
    ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")
        
    # Verify the requesting user owns the parent workspace
    ws = db.query(Workspace).filter(Workspace.id == ex.workspace_id, Workspace.user_id == user.id).first()
    if not ws:
        raise HTTPException(403, "Access denied")

    # Load persistent execution payload from storage (local JSON artifact / S3)
    storage = get_storage_service()
    result_data = None
    if ex.result_ref:
        try:
            raw_bytes = storage.retrieve_artifact(ex.result_ref)
            result_data = json.loads(raw_bytes.decode("utf-8"))
        except Exception:
            pass

    # Assemble response payload with serializable agent telemetry traces
    data = serialize_execution(ex)
    data["result"] = result_data
    data["traces"] = [serialize_trace(t) for t in ex.traces]
    return data
