"""
ReAssist ORM Models
6 normalized entities designed from the 10k DAU stress test.

Tables:
  1. users          — Identity & auth
  2. workspaces     — Research sessions (Ideation → Synthesis → Implementation)
  3. documents      — RAG file uploads linked to ChromaDB
  4. pipeline_executions — Each 7-agent run with aggregate cost/latency
  5. agent_traces   — Per-agent token & latency breakdown
  6. chat_messages  — Copilot conversation history per workspace
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class WorkspaceStatus(str, enum.Enum):
    IDEATION = "IDEATION"
    SYNTHESIS = "SYNTHESIS"
    IMPLEMENTATION = "IMPLEMENTATION"


class ExecutionType(str, enum.Enum):
    COT_BASELINE = "COT_BASELINE"
    MULTI_AGENT = "MULTI_AGENT"
    RAG_PIPELINE = "RAG_PIPELINE"


class AgentType(str, enum.Enum):
    SEARCH = "SEARCH"
    SUMMARIZE = "SUMMARIZE"
    SYNTHESIS = "SYNTHESIS"
    GAP = "GAP"
    IDEA = "IDEA"
    TECHNIQUE = "TECHNIQUE"
    IMPLEMENT = "IMPLEMENT"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


# ─── Helper ───────────────────────────────────────────────────────────────────

def gen_uuid():
    return uuid.uuid4().hex


def utcnow():
    return datetime.now(timezone.utc)


# ─── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    workspaces = relationship("Workspace", back_populates="user", cascade="all, delete-orphan")


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        Index("idx_workspace_user_updated", "user_id", "updated_at"),
    )

    id = Column(String(32), primary_key=True, default=gen_uuid)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), default="New Project")
    status = Column(Enum(WorkspaceStatus), default=WorkspaceStatus.IDEATION)
    query = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="workspaces")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    executions = relationship("PipelineExecution", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="workspace", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(32), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 for dedup (stress test recommendation)
    blob_url = Column(String(512), nullable=True)   # S3 / local path
    vector_namespace = Column(String(255), nullable=True)  # ChromaDB collection link
    uploaded_at = Column(DateTime, default=utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")


class PipelineExecution(Base):
    __tablename__ = "pipeline_executions"
    __table_args__ = (
        Index("idx_exec_workspace", "workspace_id"),
    )

    id = Column(String(32), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(32), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    execution_type = Column(Enum(ExecutionType), default=ExecutionType.MULTI_AGENT)
    total_latency_ms = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    status = Column(String(20), default="running")  # running | completed | failed
    error = Column(Text, nullable=True)
    result_ref = Column(String(512), nullable=True)  # S3 pointer for large payloads (stress test fix)
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="executions")
    traces = relationship("AgentTrace", back_populates="execution", cascade="all, delete-orphan")


class AgentTrace(Base):
    __tablename__ = "agent_traces"
    __table_args__ = (
        Index("idx_trace_exec_agent", "execution_id", "agent_type"),
    )

    id = Column(String(32), primary_key=True, default=gen_uuid)
    execution_id = Column(String(32), ForeignKey("pipeline_executions.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    response_ref = Column(String(512), nullable=True)  # Pointer, NOT inline blob (stress test fix)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    execution = relationship("PipelineExecution", back_populates="traces")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("idx_chat_workspace_time", "workspace_id", "created_at"),
    )

    id = Column(String(32), primary_key=True, default=gen_uuid)
    workspace_id = Column(String(32), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="messages")
