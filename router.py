"""
AgentRouter - AgenticOps routing layer for ReAssist
Decides whether a query should use multi-agent pipeline or CoT baseline
"""

import os
import json
from datetime import datetime


class AgentRouter:
    """
    Routes incoming queries to the appropriate execution path.
    Scores query complexity and precision to decide:
    - multi_agent: expensive, accurate, slow
    - cot: cheap, fast, good enough for simple queries
    """

    DOMAIN_JARGON = [
        "neural", "quantum", "genomic", "transformer", "diffusion",
        "federated", "adversarial", "bayesian", "contrastive",
        "autoregressive", "reinforcement", "embedding", "attention",
        "multimodal", "llm", "generative", "fine-tuning", "rag",
        "retrieval", "graph neural", "gnn", "bert", "gpt"
    ]
    COMPARISON_WORDS = [
        "vs", "versus", "compared", "difference", "tradeoff",
        "outperforms", "better than", "worse than", "benchmark"
    ]
    RECENCY_WORDS = [
        "latest", "recent", "2024", "2025", "state of the art",
        "sota", "current", "emerging", "novel"
    ]
    SURVEY_WORDS = [
        "gap", "survey", "review", "overview", "systematic",
        "landscape", "benchmark", "comprehensive", "literature"
    ]

    COSTS = {
        "gpt-3.5-turbo": {"multi_agent": 0.015, "cot": 0.004},
        "gpt-4": {"multi_agent": 0.45, "cot": 0.12},
        "gpt-4-turbo-preview": {"multi_agent": 0.30, "cot": 0.08},
    }

    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    def route(self, query: str) -> dict:
        """
        Score the query and decide which execution path to use.
        Returns a dict with decision, confidence, reasoning, and cost estimates.
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
        elif total <= 4:
            decision, confidence = "cot", 0.65
        else:
            decision, confidence = "multi_agent", 0.85

        model_costs = self.COSTS.get(self.model, self.COSTS["gpt-3.5-turbo"])
        estimated_cost = model_costs[decision]
        cost_if_always_multi = model_costs["multi_agent"]
        cost_saved = round(cost_if_always_multi - estimated_cost, 4) if decision == "cot" else 0.0

        signals_text = ", ".join(fired_signals) if fired_signals else "none"
        reasoning = (
            f"Score {total}/6. Signals: {signals_text}. "
            f"Routing to {decision} with {confidence:.0%} confidence."
        )

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "score_breakdown": {
                "complexity_score": complexity_score,
                "precision_score": precision_score,
                "total_score": total
            },
            "estimated_cost_usd": estimated_cost,
            "estimated_latency_seconds": 35 if decision == "multi_agent" else 9,
            "cost_saved_vs_always_multi_agent": cost_saved
        }

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


def create_router(model="gpt-3.5-turbo"):
    """Factory function"""
    return AgentRouter(model=model)


if __name__ == "__main__":
    router = AgentRouter()
    test_queries = [
        "transformers",
        "federated learning for medical imaging privacy",
        "latest survey on diffusion models vs GANs in image synthesis 2024"
    ]
    print("=" * 60)
    print("AGENTICOPS ROUTER TEST")
    print("=" * 60)
    for q in test_queries:
        result = router.route(q)
        router.log_decision(q, result)
        print(f"\nQuery    : {q}")
        print(f"Decision : {result['decision'].upper()} ({result['confidence']:.0%} confidence)")
        print(f"Score    : {result['score_breakdown']['total_score']}/6")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Est. cost: ${result['estimated_cost_usd']} | Saved: ${result['cost_saved_vs_always_multi_agent']}")
    print("\n" + "=" * 60)
    print("ROUTING STATS")
    print("=" * 60)
    import pprint
    pprint.pprint(router.get_stats())
