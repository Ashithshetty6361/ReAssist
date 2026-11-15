"""
================================================================================
RESUME BULLET 1 SHOWCASE: DETERMINISTIC STATE GRAPH & ORCHESTRATION
================================================================================
Resume Point:
  "Designed a deterministic 7-agent research synthesis pipeline with strict
   typed run(dict) -> dict interfaces and dynamic context slicing."

WHAT TO SHOW IN AN INTERVIEW:
  1. Show `PipelineState(TypedDict)`: The immutable data contract passed through the graph.
  2. Show how node functions enforce context slicing right before calling agents:
     - `gap_finder_node` only extracts `synthesis` from `state`.
     - `idea_generator_node` only extracts `gaps` and `synthesis` from `state`.
     - `technique_node` only extracts `synthesis` and `ideas`.
     - `guidance_node` only extracts `ideas` and `techniques`.
  3. Show the compilation into LangGraph `StateGraph(PipelineState)`.

ORIGINAL SOURCE FILES:
  - src/models/state.py
  - src/pipeline/graph_builder.py
================================================================================
"""

from typing import TypedDict, Optional, List, Any
from langgraph.graph import StateGraph, END


# 1. THE TYPED PIPELINE STATE CONTRACT
class PipelineState(TypedDict):
    """Immutable state object passed between graph nodes."""
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


# 2. DEMONSTRATION OF CONTEXT SLICING AT NODE BOUNDARIES
# (Notice how each node extracts ONLY what it needs before calling the agent!)

def gap_finder_node(state: PipelineState) -> dict:
    """GapFinderAgent receives ONLY 'synthesis', never raw papers!"""
    sliced_input = {"synthesis": state.get("synthesis", "")}
    # result = gap_finder_agent.run(sliced_input)
    # return {"gaps": result["gaps"]}
    return {"gaps": "Identified research gaps..."}


def idea_generator_node(state: PipelineState) -> dict:
    """IdeaGeneratorAgent receives ONLY 'gaps' and 'synthesis'."""
    sliced_input = {
        "gaps": state.get("gaps", ""),
        "synthesis": state.get("synthesis", "")
    }
    # result = idea_generator_agent.run(sliced_input)
    # return {"ideas": result["ideas"]}
    return {"ideas": ["Novel Idea 1", "Novel Idea 2"]}


def technique_node(state: PipelineState) -> dict:
    """TechniqueAgent receives ONLY 'synthesis' and 'ideas'."""
    sliced_input = {
        "synthesis": state.get("synthesis", ""),
        "ideas": state.get("ideas", [])
    }
    return {"techniques": "Mathematical formulations & benchmarks..."}


def guidance_node(state: PipelineState) -> dict:
    """GuidanceAgent receives ONLY 'ideas' and 'techniques'."""
    sliced_input = {
        "ideas": state.get("ideas", []),
        "techniques": state.get("techniques", "")
    }
    return {"guidance": "Phased implementation milestones..."}


# 3. HOW THE GRAPH IS COMPILED IN REASSIST
def build_showcase_graph():
    """Builds and compiles the declarative state graph."""
    graph = StateGraph(PipelineState)
    
    # Register the sequential intelligence chain
    graph.add_node("gap_finder", gap_finder_node)
    graph.add_node("idea_generator", idea_generator_node)
    graph.add_node("technique", technique_node)
    graph.add_node("guidance", guidance_node)
    
    # Connect linear edges
    graph.add_edge("gap_finder", "idea_generator")
    graph.add_edge("idea_generator", "technique")
    graph.add_edge("technique", "guidance")
    graph.add_edge("guidance", END)
    
    graph.set_entry_point("gap_finder")
    return graph.compile()


if __name__ == "__main__":
    compiled_app = build_showcase_graph()
    print("✓ Successfully compiled deterministic LangGraph state machine with context slicing!")

