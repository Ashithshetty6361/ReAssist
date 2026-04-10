"""
ReAssist FastAPI Server — Production Grade
Database-backed persistence, JWT auth, and full CRUD for workspaces & chat.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import uuid
import hashlib
from datetime import datetime, timezone
import os
import json

from sqlalchemy.orm import Session
from database import get_db, init_db
from models import (
    User, Workspace, Document, PipelineExecution, AgentTrace, ChatMessage,
    WorkspaceStatus, ExecutionType, AgentType, MessageRole
)
from auth import (
    get_current_user, create_access_token,
    hash_password, verify_password
)

from root_agent import create_root_agent
from router import create_router
from config import validate_environment, DEFAULT_MODEL, MAX_PAPERS

# Validate environment on startup
try:
    validate_environment()
except EnvironmentError as e:
    print(e)
    exit(1)

app = FastAPI(
    title="ReAssist API",
    description="Research Intelligence Engine — Multi-Agent Pipeline (Production)",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ─── Initialize DB on startup ────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class AuthRegister(BaseModel):
    email: str
    password: str

class AuthLogin(BaseModel):
    email: str
    password: str

class WorkspaceCreate(BaseModel):
    name: Optional[str] = "New Project"

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    query: Optional[str] = None

class MessageCreate(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = DEFAULT_MODEL
    max_papers: Optional[int] = MAX_PAPERS
    use_router: Optional[bool] = True
    execution_type: Optional[str] = "MULTI_AGENT"

class RouterRequest(BaseModel):
    query: str
    model: Optional[str] = DEFAULT_MODEL

class IdeateRequest(BaseModel):
    field: str
    model: Optional[str] = DEFAULT_MODEL

class CompareRequest(BaseModel):
    query: str
    model: Optional[str] = DEFAULT_MODEL


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/auth/register")
def register(req: AuthRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_access_token(user.id), "user_id": user.id}


@app.post("/auth/login")
def login(req: AuthLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_access_token(user.id), "user_id": user.id}


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "3.0.0",
        "database": "connected"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/workspaces")
def create_workspace(
    req: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = Workspace(user_id=user.id, name=req.name)
    db.add(ws)
    # Auto-create the welcome message
    welcome = ChatMessage(
        workspace_id=ws.id,
        role=MessageRole.ASSISTANT,
        content="Hello! I am ReAssist. I can help you ideate topics, run deep literature synthesis, and guide you through implementation. What are we researching today?"
    )
    db.add(welcome)
    db.commit()
    db.refresh(ws)
    return _serialize_workspace(ws)


@app.get("/workspaces")
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workspaces = (
        db.query(Workspace)
        .filter(Workspace.user_id == user.id)
        .order_by(Workspace.updated_at.desc())
        .all()
    )
    return [_serialize_workspace(ws) for ws in workspaces]


@app.get("/workspaces/{workspace_id}")
def get_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    return _serialize_workspace(ws)


@app.put("/workspaces/{workspace_id}")
def update_workspace(
    workspace_id: str,
    req: WorkspaceUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    if req.name is not None:
        ws.name = req.name
    if req.status is not None:
        ws.status = WorkspaceStatus(req.status)
    if req.query is not None:
        ws.query = req.query
    ws.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ws)
    return _serialize_workspace(ws)


@app.delete("/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    db.delete(ws)
    db.commit()
    return {"deleted": True}


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/workspaces/{workspace_id}/messages")
def get_messages(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.workspace_id == ws.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [_serialize_message(m) for m in messages]


@app.post("/workspaces/{workspace_id}/messages")
def create_message(
    workspace_id: str,
    req: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    msg = ChatMessage(
        workspace_id=ws.id,
        role=MessageRole(req.role),
        content=req.content
    )
    db.add(msg)
    ws.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)
    return _serialize_message(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE EXECUTION (DB-backed, replaces in-memory jobs dict)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/workspaces/{workspace_id}/execute")
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

    def run_pipeline():
        pdb = SessionLocal()
        try:
            start = datetime.now(timezone.utc)

            if req.use_router:
                router = create_router(model=req.model)
                routing = router.route(req.query)
                router.log_decision(req.query, routing)

            agent = create_root_agent(model=req.model, max_papers=req.max_papers)
            result = agent.execute_pipeline(query=req.query)

            end = datetime.now(timezone.utc)
            total_ms = int((end - start).total_seconds() * 1000)

            # Persist result
            ex = pdb.query(PipelineExecution).filter(PipelineExecution.id == exec_id).first()
            if ex:
                ex.status = "completed"
                ex.total_latency_ms = total_ms
                ex.completed_at = end

                # Save result to disk (stress test recommendation: no inline JSONB)
                os.makedirs("data/results", exist_ok=True)
                result_path = f"data/results/{exec_id}.json"
                with open(result_path, "w") as f:
                    json.dump(result, f, default=str)
                ex.result_ref = result_path

                # Write agent traces if available
                if isinstance(result, dict) and 'agent_timings' in result:
                    for agent_name, timing in result['agent_timings'].items():
                        trace = AgentTrace(
                            execution_id=exec_id,
                            agent_type=_map_agent_type(agent_name),
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

    # Import SessionLocal here so the background thread gets its own connection
    from database import SessionLocal
    background_tasks.add_task(run_pipeline)

    return {"execution_id": exec_id, "status": "running"}


@app.get("/workspaces/{workspace_id}/executions")
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
    return [_serialize_execution(e) for e in execs]


@app.get("/executions/{execution_id}")
def get_execution(
    execution_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not ex:
        raise HTTPException(404, "Execution not found")
    # Verify ownership
    ws = db.query(Workspace).filter(Workspace.id == ex.workspace_id, Workspace.user_id == user.id).first()
    if not ws:
        raise HTTPException(403, "Access denied")

    result_data = None
    if ex.result_ref and os.path.exists(ex.result_ref):
        with open(ex.result_ref, "r") as f:
            result_data = json.load(f)

    data = _serialize_execution(ex)
    data["result"] = result_data
    data["traces"] = [_serialize_trace(t) for t in ex.traces]
    return data


# ═══════════════════════════════════════════════════════════════════════════════
# RAG DOCUMENT UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/workspaces/{workspace_id}/documents")
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Dedup check (stress test recommendation)
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing and existing.workspace_id == ws.id:
        return {"message": "File already uploaded to this workspace", "document_id": existing.id}

    os.makedirs("data/uploads", exist_ok=True)
    blob_path = f"data/uploads/{file_hash}_{file.filename}"
    with open(blob_path, "wb") as f:
        f.write(content)

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

    return {"document_id": doc.id, "filename": doc.filename, "hash": file_hash}


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (kept for backward compat)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/route")
def route_query(request: RouterRequest):
    router = create_router(model=request.model)
    result = router.route(request.query)
    router.log_decision(request.query, result)
    return result


@app.post("/ideate")
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


@app.post("/simulate_comparison")
async def simulate_comparison(
    request: CompareRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AgenticOps Sandbox: Compare CoT baseline vs Multi-Agent pipeline."""
    # Create executions for both pipelines
    ma_exec = PipelineExecution(
        workspace_id=None,  # Sandbox is not tied to a workspace
        query=request.query,
        execution_type=ExecutionType.MULTI_AGENT,
        status="running"
    )
    # For sandbox, workspace_id is optional — we use a virtual "sandbox" workspace
    # Create a sandbox workspace if needed
    sandbox_ws = db.query(Workspace).filter(
        Workspace.user_id == user.id,
        Workspace.name == "__sandbox__"
    ).first()
    if not sandbox_ws:
        sandbox_ws = Workspace(user_id=user.id, name="__sandbox__")
        db.add(sandbox_ws)
        db.commit()
        db.refresh(sandbox_ws)

    ma_exec.workspace_id = sandbox_ws.id
    db.add(ma_exec)
    db.commit()
    db.refresh(ma_exec)

    exec_id = ma_exec.id

    def run_eval():
        from evaluation.evaluator import create_evaluator
        from database import SessionLocal
        pdb = SessionLocal()
        try:
            agent = create_root_agent(model=request.model)
            ma_result = agent.execute_pipeline(query=request.query)
            evaluator = create_evaluator(model=request.model)
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


@app.get("/stats/router")
def router_stats():
    router = create_router()
    return router.get_stats()


# ═══════════════════════════════════════════════════════════════════════════════
# SERIALIZERS
# ═══════════════════════════════════════════════════════════════════════════════

def _serialize_workspace(ws: Workspace) -> dict:
    return {
        "id": ws.id,
        "name": ws.name,
        "status": ws.status.value if ws.status else "IDEATION",
        "query": ws.query or "",
        "created_at": ws.created_at.isoformat() if ws.created_at else None,
        "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
        "message_count": len(ws.messages) if ws.messages else 0
    }


def _serialize_message(m: ChatMessage) -> dict:
    return {
        "id": m.id,
        "role": m.role.value if m.role else "assistant",
        "content": m.content,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def _serialize_execution(e: PipelineExecution) -> dict:
    return {
        "id": e.id,
        "query": e.query,
        "execution_type": e.execution_type.value if e.execution_type else "MULTI_AGENT",
        "status": e.status,
        "total_latency_ms": e.total_latency_ms,
        "total_cost_usd": e.total_cost_usd,
        "total_input_tokens": e.total_input_tokens,
        "total_output_tokens": e.total_output_tokens,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "completed_at": e.completed_at.isoformat() if e.completed_at else None,
    }


def _serialize_trace(t: AgentTrace) -> dict:
    return {
        "agent_type": t.agent_type.value if t.agent_type else "",
        "input_tokens": t.input_tokens,
        "output_tokens": t.output_tokens,
        "latency_ms": t.latency_ms,
    }


def _get_workspace_or_404(workspace_id: str, user_id: str, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


def _map_agent_type(name: str) -> AgentType:
    mapping = {
        "search": AgentType.SEARCH,
        "summarize": AgentType.SUMMARIZE,
        "summarization": AgentType.SUMMARIZE,
        "synthesis": AgentType.SYNTHESIS,
        "gap": AgentType.GAP,
        "gap_finder": AgentType.GAP,
        "idea": AgentType.IDEA,
        "idea_generator": AgentType.IDEA,
        "technique": AgentType.TECHNIQUE,
        "techniques": AgentType.TECHNIQUE,
        "implement": AgentType.IMPLEMENT,
        "implementation": AgentType.IMPLEMENT,
        "guidance": AgentType.IMPLEMENT,
    }
    return mapping.get(name.lower(), AgentType.SEARCH)


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
