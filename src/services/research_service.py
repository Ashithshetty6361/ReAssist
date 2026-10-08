"""
ReAssist — Research Service Layer
Orchestrates research pipelines, CoT baseline comparisons, traces, and DB persistence.
"""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.orm import (
    Workspace, PipelineExecution, AgentTrace, Document,
    WorkspaceStatus, ExecutionType, AgentType
)
from src.api.serializers import map_agent_type
from src.pipeline.orchestrator import create_root_agent
from src.services.storage_service import get_storage_service
from src.services.model_routing_service import get_routing_service
from src.services.observability_service import get_observability_service
from src.memory.workspace_memory import (
    load_conversation_context,
    build_context_summary,
    save_pipeline_result_as_message
)
from src.core.config import DEFAULT_MODEL, MAX_PAPERS


class ResearchService:
    """Service orchestrating AI multi-agent research pipelines and baseline evaluations."""

    def __init__(self):
        self.storage = get_storage_service()
        self.routing_service = get_routing_service()
        self.observability_service = get_observability_service()

    def run_pipeline_sync(
        self,
        workspace_id: str,
        execution_id: str,
        query: str,
        document_id: str | None = None,
        model: str | None = None,
        max_papers: int | None = None,
        use_router: bool = True,
        db: Session = None
    ) -> dict:
        """
        Synchronously execute the research pipeline and persist execution results,
        traces, and conversation memory.
        """
        model_name = model or DEFAULT_MODEL
        papers_limit = max_papers or MAX_PAPERS
        start_time = datetime.now(timezone.utc)

        # 1. Dynamic Model Routing
        routing_decision = None
        if use_router and query:
            routing_decision = self.routing_service.route_query(query)

        # 2. Conversational Memory Context
        context_summary = None
        if db:
            raw_messages = load_conversation_context(workspace_id, db)
            context_summary = build_context_summary(raw_messages)

        # 3. Agent Execution
        agent = create_root_agent(model=model_name, max_papers=papers_limit)

        if document_id and db:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                result = agent.execute_pipeline(pdf_path=doc.blob_url)
            else:
                raise ValueError("Document not found")
        else:
            result = agent.execute_pipeline(
                query=query,
                conversation_context=context_summary if context_summary else None,
            )

        end_time = datetime.now(timezone.utc)
        total_latency_ms = int((end_time - start_time).total_seconds() * 1000)

        # 4. Save chat message
        if db:
            save_pipeline_result_as_message(workspace_id, result, db)

        # 5. Persist Execution Result via StorageService
        result_json = json.dumps(result, default=str)
        storage_ref = self.storage.store_artifact(result_json, f"results/{execution_id}.json", content_type="application/json")

        # 6. Update Execution in DB & Record Traces
        if db:
            ex = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
            if ex:
                ex.status = "completed" if not result.get("error") else "failed"
                ex.total_latency_ms = total_latency_ms
                ex.completed_at = end_time
                ex.result_ref = storage_ref
                ex.error = result.get("error")

                # Record per-agent traces
                agent_timings = result.get("agent_timings", {})
                for agent_name, timing in agent_timings.items():
                    in_tok = timing.get("input_tokens", 0) if isinstance(timing, dict) else 0
                    out_tok = timing.get("output_tokens", 0) if isinstance(timing, dict) else 0
                    lat_ms = timing.get("latency_ms", int(timing * 1000)) if isinstance(timing, (dict, int, float)) else 0

                    trace = AgentTrace(
                        execution_id=execution_id,
                        agent_type=map_agent_type(agent_name),
                        input_tokens=in_tok,
                        output_tokens=out_tok,
                        latency_ms=lat_ms,
                    )
                    db.add(trace)

                db.commit()

        result["storage_ref"] = storage_ref
        result["routing"] = routing_decision
        return result


_research_service = None

def get_research_service() -> ResearchService:
    global _research_service
    if _research_service is None:
        _research_service = ResearchService()
    return _research_service
