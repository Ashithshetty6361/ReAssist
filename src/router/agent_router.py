"""
AgentRouter - Cost-Aware AgenticOps routing layer for ReAssist
Decides whether a query should use multi-agent pipeline or CoT baseline,
and dynamically selects model tiers based on task complexity.
"""

import os
import json
from datetime import datetime
from enum import Enum


class ModelTier(str, Enum):
    TIER_1_FAST = "tier_1_fast"        # Graders, Query Rewriters, Verifiers
    TIER_2_BALANCED = "tier_2_balanced"# Summarizers, Technique Agent, Guidance Agent
    TIER_3_FRONTIER = "tier_3_frontier"# Literature Synthesizer, Gap Finder, Idea Generator


# Model mappings per provider per tier
TIER_MODELS = {
    "openai": {
        ModelTier.TIER_1_FAST: "gpt-4o-mini",
        ModelTier.TIER_2_BALANCED: "gpt-4o-mini",
        ModelTier.TIER_3_FRONTIER: "gpt-4o",
    },
    "bedrock": {
        ModelTier.TIER_1_FAST: "anthropic.claude-3-haiku-20240307-v1:0",
        ModelTier.TIER_2_BALANCED: "anthropic.claude-3-5-sonnet-20240620-v1:0",
        ModelTier.TIER_3_FRONTIER: "anthropic.claude-3-5-sonnet-20240620-v1:0",
    },
    "ollama": {
        ModelTier.TIER_1_FAST: "phi3:mini",
        ModelTier.TIER_2_BALANCED: "llama3.1:8b-instruct-q4_K_M",
        ModelTier.TIER_3_FRONTIER: "llama3.1:8b-instruct-q4_K_M",
    },
    "huggingface": {
        ModelTier.TIER_1_FAST: "microsoft/Phi-3-mini-4k-instruct",
        ModelTier.TIER_2_BALANCED: "mistralai/Mistral-7B-Instruct-v0.3",
        ModelTier.TIER_3_FRONTIER: "mistralai/Mistral-7B-Instruct-v0.3",
    }
}


class AgentRouter:
    """
    Routes incoming queries to the appropriate execution path and selects model tiers.
    Scores query complexity and precision to decide:
    - multi_agent: expensive, accurate, multi-agent reasoning
    - cot: cheap, fast, good enough for simple queries
    """

    DOMAIN_JARGON = [
        "neural", "quantum", "genomic", "transformer", "diffusion",
        "federated", "adversarial", "bayesian", "contrastive",
        "autoregressive", "reinforcement", "embedding", "attention",
        "multimodal", "llm", "generative", "fine-tuning", "rag",
        "retrieval", "graph neural", "gnn", "bert", "gpt", "agentic"
    ]
    COMPARISON_WORDS = [
        "vs", "versus", "compared", "difference", "tradeoff",
        "outperforms", "better than", "worse than", "benchmark", "trade-off"
    ]
    RECENCY_WORDS = [
        "latest", "recent", "2024", "2025", "2026", "state of the art",
        "sota", "current", "emerging", "novel"
    ]
    SURVEY_WORDS = [
        "gap", "survey", "review", "overview", "systematic",
        "landscape", "benchmark", "comprehensive", "literature", "taxonomy"
    ]

    COSTS = {
        "gpt-3.5-turbo": {"multi_agent": 0.015, "cot": 0.004},
        "gpt-4o-mini": {"multi_agent": 0.006, "cot": 0.0015},
        "gpt-4o": {"multi_agent": 0.060, "cot": 0.015},
        "anthropic.claude-3-5-sonnet-20240620-v1:0": {"multi_agent": 0.075, "cot": 0.018},
        "anthropic.claude-3-haiku-20240307-v1:0": {"multi_agent": 0.008, "cot": 0.002},
        "ollama-local": {"multi_agent": 0.0, "cot": 0.0},
    }

    def __init__(self, model="gpt-3.5-turbo", provider="openai"):
        self.model = model
        self.provider = provider

    def route(self, query: str) -> dict:
        """
        Score the query and decide which execution path and model tier to use.
        Returns a dict with decision, confidence, reasoning, tier allocations, and cost estimates.
        """
        q = query.lower()
        complexity_score = 0
        precision_score = 0
        fired_signals = []

        if any(word in q for word in self.DOMAIN_JARGON):
            complexity_score += 1
            fired_signals.append("domain jargon detected")
        if len(query.split()) > 8:
            complexity_score += 1
            fired_signals.append(f"long query ({len(query.split())} words)")
        if any(word in q for word in self.COMPARISON_WORDS):
            complexity_score += 1
            fired_signals.append("comparison language detected")

        if any(word in q for word in self.RECENCY_WORDS):
            precision_score += 1
            fired_signals.append("recency keyword detected")
        if any(word in q for word in self.SURVEY_WORDS):
            precision_score += 1
            fired_signals.append("survey or gap language detected")
        if len(set(q.split())) < 6:
            precision_score += 1
            fired_signals.append("narrow specific topic")

        total = complexity_score + precision_score

        if total <= 2:
            decision, confidence = "cot", 0.90
            suggested_tier = ModelTier.TIER_1_FAST
        elif total <= 4:
            decision, confidence = "cot", 0.65
            suggested_tier = ModelTier.TIER_2_BALANCED
        else:
            decision, confidence = "multi_agent", 0.85
            suggested_tier = ModelTier.TIER_3_FRONTIER

        model_costs = self.COSTS.get(self.model, self.COSTS.get("gpt-4o-mini", {"multi_agent": 0.006, "cot": 0.0015}))
        estimated_cost = model_costs[decision]
        cost_if_always_multi = model_costs["multi_agent"]
        cost_saved = round(cost_if_always_multi - estimated_cost, 4) if decision == "cot" else 0.0

        signals_text = ", ".join(fired_signals) if fired_signals else "none"
        reasoning = (
            f"Score {total}/6. Signals: {signals_text}. "
            f"Routing to {decision} ({suggested_tier.value}) with {confidence:.0%} confidence."
        )

        provider_map = TIER_MODELS.get(self.provider, TIER_MODELS["openai"])

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "suggested_tier": suggested_tier.value,
            "tier_dispatch": {
                "fast_model": provider_map[ModelTier.TIER_1_FAST],
                "balanced_model": provider_map[ModelTier.TIER_2_BALANCED],
                "frontier_model": provider_map[ModelTier.TIER_3_FRONTIER],
            },
            "score_breakdown": {
                "complexity_score": complexity_score,
                "precision_score": precision_score,
                "total_score": total
            },
            "estimated_cost_usd": estimated_cost,
            "estimated_latency_seconds": 35 if decision == "multi_agent" else 9,
            "cost_saved_vs_always_multi_agent": cost_saved
        }

    def get_model_for_agent(self, agent_name: str, query_complexity: int = 3) -> str:
        """
        Dynamically assign the most cost-effective model tier for a specific agent.
        """
        provider_map = TIER_MODELS.get(self.provider, TIER_MODELS["openai"])
        tier_1_agents = {"grader", "rewriter", "verifier", "search_optimizer"}
        tier_3_agents = {"synthesizer", "gap_finder", "idea_generator"}

        name = agent_name.lower().replace("_agent", "").replace("agent", "")
        if name in tier_1_agents:
            return provider_map[ModelTier.TIER_1_FAST]
        elif name in tier_3_agents and query_complexity >= 4:
            return provider_map[ModelTier.TIER_3_FRONTIER]
        return provider_map[ModelTier.TIER_2_BALANCED]

    def log_decision(self, query: str, result: dict) -> None:
        """Append routing decision to logs/routing_log.jsonl"""
        os.makedirs("logs", exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            **result
        }
        try:
            with open("logs/routing_log.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Warning: Could not write routing log: {e}")

    def get_stats(self) -> dict:
        """Read routing_log.jsonl and return cost-savings statistics"""
        records = []
        try:
            with open("logs/routing_log.jsonl", "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except FileNotFoundError:
            pass

        if not records:
            return {
                "total_queries": 0,
                "multi_agent_count": 0,
                "cot_count": 0,
                "pct_multi_agent": 0.0,
                "pct_cot": 0.0,
                "total_actual_cost_usd": 0.0,
                "total_cost_if_always_multi_agent_usd": 0.0,
                "total_cost_saved_usd": 0.0,
                "avg_confidence": 0.0
            }

        total = len(records)
        ma_count = sum(1 for r in records if r.get("decision") == "multi_agent")
        cot_count = total - ma_count
        actual_cost = sum(r.get("estimated_cost_usd", 0) for r in records)
        always_multi = sum(
            r.get("estimated_cost_usd", 0) + r.get("cost_saved_vs_always_multi_agent", 0)
            for r in records
        )
        avg_conf = sum(r.get("confidence", 0) for r in records) / total

        return {
            "total_queries": total,
            "multi_agent_count": ma_count,
            "cot_count": cot_count,
            "pct_multi_agent": round(ma_count / total * 100, 1),
            "pct_cot": round(cot_count / total * 100, 1),
            "total_actual_cost_usd": round(actual_cost, 4),
            "total_cost_if_always_multi_agent_usd": round(always_multi, 4),
            "total_cost_saved_usd": round(always_multi - actual_cost, 4),
            "avg_confidence": round(avg_conf, 2)
        }


def create_router(model="gpt-3.5-turbo", provider="openai"):
    """Factory function"""
    return AgentRouter(model=model, provider=provider)
