"""
Pipeline execution routes — Execute + List + Get
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
import json

from src.core.database import get_db, SessionLocal
from src.core.auth import get_current_user
from src.models.orm import (
    User, Workspace, PipelineExecution, AgentTrace,
    WorkspaceStatus, ExecutionType
)
from src.api.schemas import QueryRequest
from src.api.serializers import (
    serialize_execution, serialize_trace, map_agent_type
)
from src.pipeline.orchestrator import create_root_agent
from src.router.agent_router import create_router
from src.core.config import DEFAULT_MODEL, MAX_PAPERS
from src.memory.workspace_memory import (
    load_conversation_context,
    build_context_summary,
    save_pipeline_result_as_message
)

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
        execution_type=ExecutionType(req.execution_type),
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
            start = datetime.now(timezone.utc)

            if req.use_router:
                agent_router = create_router(model=model)
                routing = agent_router.route(req.query)
                agent_router.log_decision(req.query, routing)

            # --- PHASE 4: Load Conversational Context ---
            context = load_conversation_context(ws.id, pdb)

            agent = create_root_agent(model=model, max_papers=max_papers)
            result = agent.execute_pipeline(query=req.query, conversation_context=context)

            # --- PHASE 4: Save Result ---
            save_pipeline_result_as_message(ws.id, result, pdb)

            end = datetime.now(timezone.utc)
            total_ms = int((end - start).total_seconds() * 1000)

            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "completed"
                ex.total_latency_ms = total_ms
                ex.completed_at = end

                os.makedirs("data/results", exist_ok=True)
                result_path = f"data/results/{exec_id}.json"
                with open(result_path, "w") as f:
                    json.dump(result, f, default=str)
                ex.result_ref = result_path

                if isinstance(result, dict) and 'agent_timings' in result:
                    for agent_name, timing in result['agent_timings'].items():
                        trace = AgentTrace(
                            execution_id=exec_id,
                            agent_type=map_agent_type(agent_name),
                            input_tokens=timing.get('input_tokens', 0),
                            output_tokens=timing.get('output_tokens', 0),
                            latency_ms=timing.get('latency_ms', 0),
                        )
                        pdb.add(trace)

                pdb.commit()
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

    result_data = None
    if ex.result_ref and os.path.exists(ex.result_ref):
        with open(ex.result_ref, "r") as f:
            result_data = json.load(f)

    data = serialize_execution(ex)
    data["result"] = result_data
    data["traces"] = [serialize_trace(t) for t in ex.traces]
    return data
