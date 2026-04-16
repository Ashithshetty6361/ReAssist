"""
ReAssist — LangGraph Pipeline Builder
Replaces imperative orchestration with a declarative state graph.

Graph topology:
  START -> search -> grade -> [grade_router]
    grade_router -> summarize (if enough papers)
    grade_router -> rewrite (if not enough)
  rewrite -> [rewrite_router]
    rewrite_router -> search (if attempts left — loop)
    rewrite_router -> web_search (if exhausted)
  web_search -> [web_search_router]
    web_search_router -> summarize (if papers found)
    web_search_router -> END (with error)
  summarize -> synthesize -> gap_finder -> idea_generator
    -> technique -> guidance -> verify -> END
"""

import time
from langgraph.graph import StateGraph, END

from src.models.state import PipelineState
from src.agents.search_agent import create_search_agent
from src.agents.summarize_agent import create_summarizer_agent
from src.agents.synthesize_agent import create_synthesizer_agent
from src.agents.gap_finder_agent import create_gap_finder_agent
from src.agents.idea_generator_agent import create_idea_generator_agent
from src.agents.technique_agent import create_technique_agent
from src.agents.guidance_agent import create_guidance_agent
from src.agents.relevance_grader import create_relevance_grader
from src.agents.query_rewriter import create_query_rewriter
from src.agents.answer_verifier import create_answer_verifier
from src.agents.web_search_agent import create_web_search_agent
from src.core.config import (
    RELEVANCE_THRESHOLD, MAX_QUERY_REWRITES,
    GRADER_MODEL, DEFAULT_MODEL, MAX_PAPERS
)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent singletons (created once per build)
# ═══════════════════════════════════════════════════════════════════════════════

_agents = {}


def _get_agents(model: str = DEFAULT_MODEL, max_papers: int = MAX_PAPERS):
    """Lazy-init all 11 agents and cache them."""
    key = (model, max_papers)
    if key not in _agents:
        _agents[key] = {
            "search": create_search_agent(max_papers=max_papers),
            "summarizer": create_summarizer_agent(model=model),
            "synthesizer": create_synthesizer_agent(model=model),
            "gap_finder": create_gap_finder_agent(model=model),
            "idea_generator": create_idea_generator_agent(model=model),
            "technique": create_technique_agent(model=model),
            "guidance": create_guidance_agent(model=model),
            "grader": create_relevance_grader(model=GRADER_MODEL),
            "rewriter": create_query_rewriter(model=GRADER_MODEL),
            "verifier": create_answer_verifier(model=GRADER_MODEL),
            "web_search": create_web_search_agent(),
        }
    return _agents[key]


def _run_with_retry(agent, agent_name, input_data, max_retries=2):
    """Run an agent with automatic retry on failure."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = agent.run(input_data)
            return result
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                import openai
                if isinstance(e, openai.RateLimitError):
                    time.sleep((2 ** attempt) * 5)
                elif isinstance(e, openai.APIConnectionError):
                    time.sleep(3)
                else:
                    time.sleep(2)
    raise RuntimeError(
        f"Agent '{agent_name}' failed after {max_retries + 1} attempts: {last_error}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Node functions — each takes PipelineState, returns partial state update
# ═══════════════════════════════════════════════════════════════════════════════

def search_node(state: PipelineState) -> dict:
    """Search for papers using the current query."""
    agents = _get_agents()
    start = time.time()
    input_data = {"query": state["query"], "conversation_context": state.get("conversation_context")}
    result = _run_with_retry(agents["search"], "SearchAgent", input_data)
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    rewrite_count = state.get("rewrite_count", 0)
    if rewrite_count == 0:
        timings["search"] = elapsed
    else:
        timings[f"search_rewrite_{rewrite_count}"] = elapsed

    papers = result.get("papers", []) if result.get("success") else []
    # Merge with any existing papers from previous rewrite iterations
    existing = list(state.get("papers", []))
    existing.extend(papers)

    return {"papers": existing, "agent_timings": timings}


def grade_node(state: PipelineState) -> dict:
    """Grade retrieved papers for relevance."""
    agents = _get_agents()
    start = time.time()
    result = agents["grader"].run({
        "papers": state["papers"],
        "query": state["query"]
    })
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    rc = state.get("rewrite_count", 0)
    timings[f"grading{'_r' + str(rc) if rc > 0 else ''}"] = elapsed

    if result.get("success"):
        graded_papers = result.get("papers", [])
        # Deduplicate by title
        seen = set()
        unique = []
        for p in graded_papers:
            t = p.get("title", "")
            if t not in seen:
                seen.add(t)
                unique.append(p)
        return {
            "papers": unique,
            "agent_timings": timings,
            "retrieval_quality": {
                "relevant_count": len(unique),
                "rewrites_needed": rc,
                "web_fallback_used": False,
            },
        }
    return {"agent_timings": timings}


def rewrite_node(state: PipelineState) -> dict:
    """Rewrite the query for a better search."""
    agents = _get_agents()
    rc = state.get("rewrite_count", 0)
    start = time.time()
    result = agents["rewriter"].run({"query": state["query"]})
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings[f"rewrite_{rc}"] = elapsed

    new_query = result.get("rewritten_query", state["query"]) if result.get("success") else state["query"]
    return {
        "query": new_query,
        "rewrite_count": rc + 1,
        "agent_timings": timings,
    }


def web_search_node(state: PipelineState) -> dict:
    """Fallback web search via Tavily."""
    agents = _get_agents()
    start = time.time()
    result = agents["web_search"].run({"query": state["query"]})
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["web_search_fallback"] = elapsed

    papers = list(state.get("papers", []))
    if result.get("success") and result.get("papers"):
        papers.extend(result["papers"])

    return {
        "papers": papers,
        "web_fallback_used": True,
        "agent_timings": timings,
        "retrieval_quality": {
            "relevant_count": len(papers),
            "rewrites_needed": state.get("rewrite_count", 0),
            "web_fallback_used": True,
        },
    }


def summarize_node(state: PipelineState) -> dict:
    """Summarize each paper."""
    agents = _get_agents()
    start = time.time()
    result = _run_with_retry(agents["summarizer"], "SummarizerAgent", {"papers": state["papers"]})
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["summarizer"] = elapsed

    if result.get("success"):
        return {"papers": result["papers"], "agent_timings": timings}
    return {"error": result.get("error", "Summarization failed"), "agent_timings": timings}


def synthesize_node(state: PipelineState) -> dict:
    """Cross-paper knowledge synthesis."""
    agents = _get_agents()
    start = time.time()
    input_data = {"papers": state["papers"], "conversation_context": state.get("conversation_context")}
    result = _run_with_retry(agents["synthesizer"], "SynthesizerAgent", input_data)
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["synthesizer"] = elapsed

    if result.get("success"):
        return {"synthesis": result["synthesis"], "agent_timings": timings}
    return {"error": result.get("error", "Synthesis failed"), "agent_timings": timings}


def gap_finder_node(state: PipelineState) -> dict:
    """Identify research gaps."""
    agents = _get_agents()
    start = time.time()
    result = _run_with_retry(agents["gap_finder"], "GapFinderAgent", {"synthesis": state.get("synthesis", "")})
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["gap_finder"] = elapsed

    if result.get("success"):
        return {"gaps": result["gaps"], "agent_timings": timings}
    return {"error": result.get("error", "Gap finding failed"), "agent_timings": timings}


def idea_generator_node(state: PipelineState) -> dict:
    """Generate novel research ideas."""
    agents = _get_agents()
    start = time.time()
    result = _run_with_retry(agents["idea_generator"], "IdeaGeneratorAgent", {
        "gaps": state.get("gaps", ""),
        "synthesis": state.get("synthesis", ""),
    })
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["idea_generator"] = elapsed

    if result.get("success"):
        return {"ideas": result["ideas"], "agent_timings": timings}
    return {"error": result.get("error", "Idea generation failed"), "agent_timings": timings}


def technique_node(state: PipelineState) -> dict:
    """Suggest alternative techniques."""
    agents = _get_agents()
    start = time.time()
    result = _run_with_retry(agents["technique"], "TechniqueAgent", {
        "synthesis": state.get("synthesis", ""),
        "ideas": state.get("ideas", []),
    })
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["technique"] = elapsed

    if result.get("success"):
        return {"techniques": result["techniques"], "agent_timings": timings}
    return {"error": result.get("error", "Technique suggestion failed"), "agent_timings": timings}


def guidance_node(state: PipelineState) -> dict:
    """Provide implementation guidance."""
    agents = _get_agents()
    start = time.time()
    result = _run_with_retry(agents["guidance"], "GuidanceAgent", {
        "ideas": state.get("ideas", []),
        "techniques": state.get("techniques", ""),
    })
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["guidance"] = elapsed

    if result.get("success"):
        return {"guidance": result["guidance"], "agent_timings": timings}
    return {"error": result.get("error", "Guidance failed"), "agent_timings": timings}


def verify_node(state: PipelineState) -> dict:
    """Verify synthesis faithfulness (hallucination guard)."""
    agents = _get_agents()
    start = time.time()
    result = agents["verifier"].run({
        "synthesis": state.get("synthesis", ""),
        "papers": state.get("papers", []),
        "gaps": state.get("gaps", ""),
    })
    elapsed = time.time() - start

    timings = dict(state.get("agent_timings", {}))
    timings["verification"] = elapsed

    verification = {
        "faithful": result.get("faithful", True),
        "confidence": result.get("confidence", 0.0),
        "unsupported_claims": result.get("unsupported_claims", []),
        "summary": result.get("verification_summary", ""),
    }
    return {"verification": verification, "agent_timings": timings}


# ═══════════════════════════════════════════════════════════════════════════════
# Conditional edge routers
# ═══════════════════════════════════════════════════════════════════════════════

def grade_router(state: PipelineState) -> str:
    """After grading: enough papers? -> summarize, not enough? -> rewrite."""
    relevant = len(state.get("papers", []))
    if relevant >= RELEVANCE_THRESHOLD:
        return "summarize_node"
    return "rewrite_node"


def rewrite_router(state: PipelineState) -> str:
    """After rewriting: attempts left? -> search again, exhausted? -> web_search."""
    if state.get("rewrite_count", 0) < MAX_QUERY_REWRITES:
        return "search_node"
    return "web_search_node"


def web_search_router(state: PipelineState) -> str:
    """After web search: found papers? -> summarize, nothing? -> END."""
    if state.get("papers"):
        return "summarize_node"
    return END


def error_check(state: PipelineState) -> str:
    """Check if an error occurred at any stage — short-circuit to END."""
    if state.get("error"):
        return END
    return "continue"


# ═══════════════════════════════════════════════════════════════════════════════
# Graph builder
# ═══════════════════════════════════════════════════════════════════════════════

def build_pipeline_graph() -> StateGraph:
    """Build and compile the full LangGraph pipeline."""
    graph = StateGraph(PipelineState)

    # Register all nodes
    graph.add_node("search_node", search_node)
    graph.add_node("grade_node", grade_node)
    graph.add_node("rewrite_node", rewrite_node)
    graph.add_node("web_search_node", web_search_node)
    graph.add_node("summarize_node", summarize_node)
    graph.add_node("synthesize_node", synthesize_node)
    graph.add_node("gap_finder_node", gap_finder_node)
    graph.add_node("idea_generator_node", idea_generator_node)
    graph.add_node("technique_node", technique_node)
    graph.add_node("guidance_node", guidance_node)
    graph.add_node("verify_node", verify_node)

    # ─── Entry ───────────────────────────────────────────────────────────
    graph.set_entry_point("search_node")

    # ─── Search -> Grade -> [grade_router] ───────────────────────────────
    graph.add_edge("search_node", "grade_node")
    graph.add_conditional_edges("grade_node", grade_router, {
        "summarize_node": "summarize_node",
        "rewrite_node": "rewrite_node",
    })

    # ─── Rewrite -> [rewrite_router] ─────────────────────────────────────
    graph.add_conditional_edges("rewrite_node", rewrite_router, {
        "search_node": "search_node",
        "web_search_node": "web_search_node",
    })

    # ─── Web search -> [web_search_router] ───────────────────────────────
    graph.add_conditional_edges("web_search_node", web_search_router, {
        "summarize_node": "summarize_node",
        END: END,
    })

    # ─── Linear pipeline: summarize -> ... -> verify -> END ──────────────
    graph.add_edge("summarize_node", "synthesize_node")
    graph.add_edge("synthesize_node", "gap_finder_node")
    graph.add_edge("gap_finder_node", "idea_generator_node")
    graph.add_edge("idea_generator_node", "technique_node")
    graph.add_edge("technique_node", "guidance_node")
    graph.add_edge("guidance_node", "verify_node")
    graph.add_edge("verify_node", END)

    return graph.compile()


# Pre-built graph singleton
pipeline_graph = build_pipeline_graph()
