"""
ReAssist — LangGraph Pipeline State
TypedDict defining the state that flows through the LangGraph pipeline.
"""

from typing import TypedDict, Optional, List, Any


class PipelineState(TypedDict):
    """State object passed between LangGraph nodes."""
    query: str
    mode: str                                   # "query" | "pdf"
    papers: List[dict]
    synthesis: Optional[str]
    gaps: Optional[str]
    ideas: Optional[Any]
    techniques: Optional[str]
    guidance: Optional[str]
    verification: Optional[dict]
    retrieval_quality: Optional[dict]
    agent_timings: dict
    rewrite_count: int
    web_fallback_used: bool
    error: Optional[str]
    conversation_context: Optional[List[dict]]  # Phase 4: memory
