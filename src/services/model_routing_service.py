"""
ReAssist — Model Routing Service Layer
Handles dynamic cost-aware model routing and per-agent tier assignment.
"""

from src.router.agent_router import create_router, AgentRouter
from src.core.llm_provider import get_provider, get_default_model


class ModelRoutingService:
    """Service encapsulating cost-aware model routing logic."""

    def __init__(self, default_model: str | None = None, provider: str | None = None):
        self.provider = provider or get_provider()
        self.default_model = default_model or get_default_model(self.provider)
        self.router = create_router(model=self.default_model, provider=self.provider)

    def route_query(self, query: str, log_decision: bool = True) -> dict:
        """Route a user query and determine execution path & suggested model tiers."""
        decision = self.router.route(query)
        if log_decision:
            self.router.log_decision(query, decision)
        return decision

    def get_agent_model(self, agent_name: str, query_complexity: int = 3) -> str:
        """Get the optimal model for an individual agent in the pipeline."""
        return self.router.get_model_for_agent(agent_name, query_complexity=query_complexity)

    def get_routing_stats(self) -> dict:
        """Retrieve aggregated cost-savings statistics."""
        return self.router.get_stats()


_routing_service = None

def get_routing_service() -> ModelRoutingService:
    global _routing_service
    if _routing_service is None:
        _routing_service = ModelRoutingService()
    return _routing_service
