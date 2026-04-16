"""
ReAssist — Pydantic Request/Response Schemas
All API input/output models in one place.
"""

from pydantic import BaseModel
from typing import Optional


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
    model: Optional[str] = None
    max_papers: Optional[int] = None
    use_router: Optional[bool] = True
    execution_type: Optional[str] = "MULTI_AGENT"


class RouterRequest(BaseModel):
    query: str
    model: Optional[str] = None


class IdeateRequest(BaseModel):
    field: str
    model: Optional[str] = None


class CompareRequest(BaseModel):
    query: str
    model: Optional[str] = None
