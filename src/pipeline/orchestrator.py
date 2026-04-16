"""
Root Agent — Thin orchestrator wrapping the LangGraph pipeline.
Preserved: PDF mode, observability reports, performance summaries.
The imperative if/else chain is GONE — replaced by graph_builder.pipeline_graph.
"""

import os
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

from src.pipeline.graph_builder import pipeline_graph, _get_agents
from src.models.state import PipelineState
from src.core.config import GRADER_MODEL
from src.utils.logger import get_logger, reset_logger

load_dotenv()


class PipelineError(Exception):
    """Raised when a pipeline stage fails after all retries"""
    pass


class RootAgent:
    """
    Root Orchestrator Agent — v3.1 (LangGraph-backed)
    
    Responsibilities:
    - Build initial PipelineState and invoke the LangGraph pipeline
    - Handle PDF-upload mode separately (same agents, different entry)
    - Build observability report after each run
    - Save structured logs
    """

    def __init__(self, model="gpt-3.5-turbo", max_papers=5):
        self.model = model
        self.max_papers = max_papers
        self.logger = reset_logger()
        self.agent_timings = {}

        # Pre-warm the agent cache so graph nodes use the right model
        _get_agents(model=model, max_papers=max_papers)

        self.logger.logger.info("Root Agent initialized (LangGraph pipeline, 11 agents)")

    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════════

    def execute_pipeline(self, query=None, pdf_path=None, conversation_context=None):
        """
        Execute the research pipeline.
        - query mode: search -> grade -> rewrite loop -> synthesize chain
        - pdf mode:   extract -> summarize chain (no search)
        """
        if pdf_path:
            return self._execute_pdf_mode(pdf_path)
        elif query:
            return self._execute_query_mode(query, conversation_context=conversation_context)
        else:
            return {"error": "Must provide either query or pdf_path", "success": False}

    def get_performance_summary(self):
        """Return timing data for the last run."""
        return {
            "agent_timings": self.agent_timings,
            "total_time": sum(self.agent_timings.values()),
            "log_summary": self.logger.get_log_summary(),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # QUERY MODE — delegates entirely to LangGraph
    # ═══════════════════════════════════════════════════════════════════════════

    def _execute_query_mode(self, query: str, conversation_context=None) -> dict:
        self.logger.log_query(query)
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("STARTING LANGGRAPH ADAPTIVE PIPELINE (QUERY MODE)")
        self.logger.logger.info("=" * 80)

        # Build initial state
        initial_state: PipelineState = {
            "query": query,
            "mode": "query",
            "papers": [],
            "synthesis": None,
            "gaps": None,
            "ideas": None,
            "techniques": None,
            "guidance": None,
            "verification": None,
            "retrieval_quality": None,
            "agent_timings": {},
            "rewrite_count": 0,
            "web_fallback_used": False,
            "error": None,
            "conversation_context": conversation_context,
        }

        # Invoke the compiled LangGraph pipeline
        try:
            final_state = pipeline_graph.invoke(initial_state)
        except Exception as e:
            self.logger.log_error(f"Pipeline failed: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "papers": [],
                "agent_timings": {},
            }

        # Extract results from final state
        self.agent_timings = final_state.get("agent_timings", {})

        # Log timings
        total_time = sum(self.agent_timings.values())
        self.logger.logger.info("\n" + "=" * 80)
        self.logger.logger.info(f"LANGGRAPH PIPELINE COMPLETED (Total: {total_time:.2f}s)")
        self.logger.logger.info("=" * 80)
        for name, dur in self.agent_timings.items():
            self.logger.logger.info(f"  {name}: {dur:.2f}s")
        self.logger.save_json_log()

        # Build result dict (same shape the API expects)
        results = {
            "query": query,
            "papers": final_state.get("papers", []),
            "synthesis": final_state.get("synthesis"),
            "gaps": final_state.get("gaps"),
            "ideas": final_state.get("ideas"),
            "techniques": final_state.get("techniques"),
            "guidance": final_state.get("guidance"),
            "verification": final_state.get("verification"),
            "retrieval_quality": final_state.get("retrieval_quality"),
            "error": final_state.get("error"),
            "agent_timings": self.agent_timings,
        }

        # Build observability report
        run_id = uuid.uuid4().hex[:8]
        results["observability"] = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "total_time_seconds": round(total_time, 2),
            "agent_timings": {k: round(v, 2) for k, v in self.agent_timings.items()},
            "slowest_agent": max(self.agent_timings, key=self.agent_timings.get)
                if self.agent_timings else None,
            "papers_found": len(results.get("papers", [])),
            "ideas_generated": len(results.get("ideas", []))
                if isinstance(results.get("ideas"), list) else 0,
            "pipeline_success": results.get("error") is None,
            "retrieval_quality": results.get("retrieval_quality"),
            "verification": results.get("verification"),
        }

        # Save observability report
        os.makedirs("logs/runs", exist_ok=True)
        report_path = f"logs/runs/run_{run_id}.json"
        with open(report_path, "w") as f:
            json.dump(results["observability"], f, indent=2)
        self.logger.logger.info(f"Observability report: {report_path}")

        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # PDF MODE — kept separate (no search/grade/rewrite)
    # ═══════════════════════════════════════════════════════════════════════════

    def _execute_pdf_mode(self, pdf_path: str) -> dict:
        from src.utils.pdf_parser import extract_text_from_pdf, create_paper_dict_from_pdf

        self.logger.logger.info("=" * 80)
        self.logger.logger.info("STARTING PIPELINE (PDF UPLOAD MODE)")
        self.logger.logger.info("=" * 80)

        results = {
            "mode": "pdf_upload",
            "pdf_path": pdf_path,
            "papers": [],
            "synthesis": None,
            "gaps": None,
            "ideas": None,
            "techniques": None,
            "guidance": None,
            "verification": None,
            "error": None,
            "agent_timings": {},
        }

        agents = _get_agents(model=self.model, max_papers=self.max_papers)

        try:
            # Extract PDF
            start = time.time()
            pdf_extract = extract_text_from_pdf(pdf_path)
            self.agent_timings["pdf_extraction"] = time.time() - start

            if not pdf_extract["success"]:
                results["error"] = pdf_extract["error"]
                return results

            paper = create_paper_dict_from_pdf(pdf_path, pdf_extract)
            results["papers"] = [paper]

            # Summarize -> Synthesize -> Gaps -> Ideas -> Technique -> Guidance -> Verify
            stage_sequence = [
                ("summarizer", {"papers": results["papers"]}, "papers", lambda r: r["papers"]),
                ("synthesizer", lambda: {"papers": results["papers"]}, "synthesis", lambda r: r["synthesis"]),
                ("gap_finder", lambda: {"synthesis": results["synthesis"]}, "gaps", lambda r: r["gaps"]),
                ("idea_generator", lambda: {"gaps": results["gaps"], "synthesis": results["synthesis"]}, "ideas", lambda r: r["ideas"]),
                ("technique", lambda: {"synthesis": results["synthesis"], "ideas": results["ideas"]}, "techniques", lambda r: r["techniques"]),
                ("guidance", lambda: {"ideas": results["ideas"], "techniques": results["techniques"]}, "guidance", lambda r: r["guidance"]),
            ]

            for agent_name, input_fn, result_key, extractor in stage_sequence:
                start = time.time()
                inp = input_fn() if callable(input_fn) else input_fn
                agent_result = agents[agent_name].run(inp)
                self.agent_timings[agent_name] = time.time() - start

                if not agent_result.get("success"):
                    results["error"] = agent_result.get("error")
                    return results
                results[result_key] = extractor(agent_result)

            # Verify
            start = time.time()
            verify_result = agents["verifier"].run({
                "synthesis": results["synthesis"],
                "papers": results["papers"],
                "gaps": results["gaps"],
            })
            self.agent_timings["verification"] = time.time() - start
            results["verification"] = {
                "faithful": verify_result.get("faithful", True),
                "confidence": verify_result.get("confidence", 0.0),
                "unsupported_claims": verify_result.get("unsupported_claims", []),
                "summary": verify_result.get("verification_summary", ""),
            }

            results["agent_timings"] = self.agent_timings
            total = sum(self.agent_timings.values())
            self.logger.logger.info(f"PDF ANALYSIS COMPLETED (Total: {total:.2f}s)")
            self.logger.save_json_log()

        except Exception as e:
            self.logger.log_error(f"PDF pipeline failed: {str(e)}")
            results["error"] = str(e)

        return results


def create_root_agent(model="gpt-3.5-turbo", max_papers=5):
    """Factory function to create root agent."""
    return RootAgent(model=model, max_papers=max_papers)
