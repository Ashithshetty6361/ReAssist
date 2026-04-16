"""
Legacy endpoints — /route, /ideate, /simulate_comparison, /stats
Kept for backward compatibility.
"""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
import json

from src.core.database import get_db, SessionLocal
from src.core.auth import get_current_user
from src.core.config import DEFAULT_MODEL
from src.models.orm import (
    User, Workspace, PipelineExecution, ExecutionType
)
from src.api.schemas import RouterRequest, IdeateRequest, CompareRequest
from src.pipeline.orchestrator import create_root_agent
from src.router.agent_router import create_router

router = APIRouter(tags=["legacy"])


@router.post("/route")
def route_query(request: RouterRequest):
    agent_router = create_router(model=request.model or DEFAULT_MODEL)
    result = agent_router.route(request.query)
    agent_router.log_decision(request.query, result)
    return result


@router.post("/ideate")
def ideate_topics(request: IdeateRequest):
    import openai
    try:
        response = openai.ChatCompletion.create(
            model=request.model or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a research ideation bot. Given a broad field, output 3 highly niche, compelling research topics with 1 sentence explaining their novelty. Output ONLY a valid JSON array of strings."},
                {"role": "user", "content": f"Field: {request.field}"}
            ]
        )
        content = response.choices[0].message.content
        try:
            topics = json.loads(content)
        except Exception:
            topics = [content]
        return {"success": True, "topics": topics}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/simulate_comparison")
async def simulate_comparison(
    request: CompareRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AgenticOps Sandbox: Compare CoT baseline vs Multi-Agent pipeline."""
    sandbox_ws = db.query(Workspace).filter(
        Workspace.user_id == user.id,
        Workspace.name == "__sandbox__"
    ).first()
    if not sandbox_ws:
        sandbox_ws = Workspace(user_id=user.id, name="__sandbox__")
        db.add(sandbox_ws)
        db.commit()
        db.refresh(sandbox_ws)

    ma_exec = PipelineExecution(
        workspace_id=sandbox_ws.id,
        query=request.query,
        execution_type=ExecutionType.MULTI_AGENT,
        status="running"
    )
    db.add(ma_exec)
    db.commit()
    db.refresh(ma_exec)

    exec_id = ma_exec.id
    model = request.model or DEFAULT_MODEL

    def run_eval():
        from evaluation.evaluator import create_evaluator
        pdb = SessionLocal()
        try:
            agent = create_root_agent(model=model)
            ma_result = agent.execute_pipeline(query=request.query)
            evaluator = create_evaluator(model=model)
            comparison = evaluator.run_baseline_comparison(
                request.query, ma_result.get('papers', []), ma_result
            )

            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "completed"
                ex.completed_at = datetime.now(timezone.utc)
                os.makedirs("data/results", exist_ok=True)
                path = f"data/results/{exec_id}.json"
                with open(path, "w") as f:
                    json.dump(comparison, f, default=str)
                ex.result_ref = path
                pdb.commit()
        except Exception as e:
            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "failed"
                ex.error = str(e)
                pdb.commit()
        finally:
            pdb.close()

    background_tasks.add_task(run_eval)
    return {"execution_id": exec_id, "status": "running"}


@router.get("/stats/router")
def router_stats():
    agent_router = create_router()
    return agent_router.get_stats()
