"""
Observability routes — Real-time telemetry, latency metrics, and run traces
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.orm import User, PipelineExecution, AgentTrace
from src.api.serializers import serialize_trace
from src.services.observability_service import get_observability_service
from src.services.model_routing_service import get_routing_service

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/stats")
def get_system_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return overall pipeline latency, token usage, and cost-savings statistics."""
    routing_stats = get_routing_service().get_routing_stats()
    obs_service = get_observability_service()

    total_executions = db.query(PipelineExecution).count()
    completed_executions = db.query(PipelineExecution).filter(PipelineExecution.status == "completed").count()
    failed_executions = db.query(PipelineExecution).filter(PipelineExecution.status == "failed").count()

    recent_runs = obs_service.list_recent_runs(limit=10)

    return {
        "executions": {
            "total": total_executions,
            "completed": completed_executions,
            "failed": failed_executions,
        },
        "routing": routing_stats,
        "recent_runs": recent_runs,
    }


@router.get("/runs/{run_id}")
def get_run_report(
    run_id: str,
    user: User = Depends(get_current_user)
):
    """Retrieve detailed per-agent observability report for a specific run ID."""
    report = get_observability_service().get_run_report(run_id)
    if not report:
        raise HTTPException(404, f"Observability report for run_id '{run_id}' not found")
    return report


@router.get("/executions/{execution_id}/traces")
def get_execution_traces(
    execution_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get per-agent execution traces with latency and token breakdowns."""
    ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")

    traces = db.query(AgentTrace).filter(AgentTrace.execution_id == execution_id).all()
    return {
        "execution_id": execution_id,
        "total_latency_ms": ex.total_latency_ms,
        "status": ex.status,
        "traces": [serialize_trace(t) for t in traces]
    }
