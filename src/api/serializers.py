"""
ReAssist — ORM-to-dict serializers for API responses.
"""

from src.models.orm import (
    Workspace, ChatMessage, PipelineExecution, AgentTrace, AgentType
)


def serialize_workspace(ws: Workspace) -> dict:
    return {
        "id": ws.id,
        "name": ws.name,
        "status": ws.status.value if ws.status else "IDEATION",
        "query": ws.query or "",
        "created_at": ws.created_at.isoformat() if ws.created_at else None,
        "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
        "message_count": len(ws.messages) if ws.messages else 0
    }


def serialize_message(m: ChatMessage) -> dict:
    return {
        "id": m.id,
        "role": m.role.value if m.role else "assistant",
        "content": m.content,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def serialize_execution(e: PipelineExecution) -> dict:
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


def serialize_trace(t: AgentTrace) -> dict:
    return {
        "agent_type": t.agent_type.value if t.agent_type else "",
        "input_tokens": t.input_tokens,
        "output_tokens": t.output_tokens,
        "latency_ms": t.latency_ms,
    }


def map_agent_type(name: str) -> AgentType:
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
