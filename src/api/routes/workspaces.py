"""
Workspace CRUD + Chat Messages routes
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.core.database import get_db
from src.core.auth import get_current_user
from src.models.orm import (
    User, Workspace, ChatMessage,
    WorkspaceStatus, MessageRole
)
from src.api.schemas import WorkspaceCreate, WorkspaceUpdate, MessageCreate
from src.api.serializers import serialize_workspace, serialize_message

router = APIRouter(tags=["workspaces"])


def _get_workspace_or_404(workspace_id: str, user_id: str, db: Session) -> Workspace:
    ws = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


# ═══ Workspace CRUD ═══════════════════════════════════════════════════════════

@router.post("/workspaces")
def create_workspace(
    req: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = Workspace(user_id=user.id, name=req.name)
    db.add(ws)
    welcome = ChatMessage(
        workspace_id=ws.id,
        role=MessageRole.ASSISTANT,
        content="Hello! I am ReAssist. I can help you ideate topics, run deep literature synthesis, and guide you through implementation. What are we researching today?"
    )
    db.add(welcome)
    db.commit()
    db.refresh(ws)
    return serialize_workspace(ws)


@router.get("/workspaces")
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
    return [serialize_workspace(ws) for ws in workspaces]


@router.get("/workspaces/{workspace_id}")
def get_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    return serialize_workspace(ws)


@router.put("/workspaces/{workspace_id}")
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
    return serialize_workspace(ws)


@router.delete("/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    db.delete(ws)
    db.commit()
    return {"deleted": True}


# ═══ Chat Messages ════════════════════════════════════════════════════════════

@router.get("/workspaces/{workspace_id}/messages")
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
    return [serialize_message(m) for m in messages]


@router.post("/workspaces/{workspace_id}/messages")
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
    return serialize_message(msg)
