"""
ReAssist — Conversational Memory Layer
Loads prior chat messages from the DB to give the pipeline conversation context.
"""

from sqlalchemy.orm import Session
from src.models.orm import ChatMessage, MessageRole


def load_conversation_context(
    workspace_id: str, db: Session, max_messages: int = 20
) -> list[dict]:
    """
    Load the last N chat messages as conversation context.

    Args:
        workspace_id: The workspace to load messages from
        db: SQLAlchemy session
        max_messages: Max messages to load (newest first, then reversed)

    Returns:
        List of {"role": str, "content": str} dicts, oldest first
    """
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.workspace_id == workspace_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(max_messages)
        .all()
    )
    messages.reverse()  # Oldest first
    return [{"role": m.role.value, "content": m.content} for m in messages]


def build_context_summary(messages: list[dict]) -> str:
    """
    Build a natural language summary of the conversation so far.

    Args:
        messages: List of {"role": str, "content": str}

    Returns:
        A formatted string of the last 10 messages, or empty string
    """
    if not messages:
        return ""
    parts = []
    for m in messages[-10:]:  # Last 10 messages
        parts.append(f"{m['role'].upper()}: {m['content'][:200]}")
    return "Previous conversation:\n" + "\n".join(parts)


def save_pipeline_result_as_message(
    workspace_id: str, result: dict, db: Session
) -> None:
    """
    Save the pipeline's synthesis as an assistant message in the chat history.

    Args:
        workspace_id: Target workspace
        result: Pipeline result dict
        db: SQLAlchemy session
    """
    content = result.get("synthesis", "") or str(result)
    msg = ChatMessage(
        workspace_id=workspace_id,
        role=MessageRole.ASSISTANT,
        content=content[:5000],
    )
    db.add(msg)
    db.commit()
