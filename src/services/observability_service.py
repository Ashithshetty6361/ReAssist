"""
ReAssist — Observability Service Layer
Aggregates per-agent latency breakdowns, token counting, cost tracking, and execution traces.
"""

import os
import json
from typing import Dict, Any, List
from src.utils.cost_projector import project_costs, calculate_cost


class ObservabilityService:
    """Service providing runtime telemetry and observability analytics for AI agent runs."""

    def format_agent_telemetry(self, agent_timings: dict, model_name: str = "gpt-4o-mini") -> dict:
        """Format raw agent timings and calculate latency + token metrics."""
        formatted_traces = []
        total_latency_ms = 0
        total_input_tokens = 0
        total_output_tokens = 0

        for agent_name, timing in agent_timings.items():
            if isinstance(timing, dict):
                lat = timing.get("latency_ms", 0)
                in_tok = timing.get("input_tokens", 0)
                out_tok = timing.get("output_tokens", 0)
            elif isinstance(timing, (int, float)):
                lat = int(timing * 1000)
                in_tok = 0
                out_tok = 0
            else:
                continue

            total_latency_ms += lat
            total_input_tokens += in_tok
            total_output_tokens += out_tok

            formatted_traces.append({
                "agent_name": agent_name,
                "latency_ms": lat,
                "latency_seconds": round(lat / 1000.0, 2),
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "cost_usd": calculate_cost(in_tok, out_tok, model_name),
            })

        cost_usd = calculate_cost(total_input_tokens, total_output_tokens, model_name)
        cost_projections = project_costs(total_input_tokens, total_output_tokens) if (total_input_tokens + total_output_tokens) > 0 else {}

        return {
            "total_latency_ms": total_latency_ms,
            "total_latency_seconds": round(total_latency_ms / 1000.0, 2),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost_usd": cost_usd,
            "traces": formatted_traces,
            "cost_projections": cost_projections,
        }

    def get_run_report(self, run_id: str) -> dict | None:
        """Fetch saved run report from logs/runs/."""
        path = f"logs/runs/run_{run_id}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_recent_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List summary of recent execution runs."""
        runs_dir = "logs/runs"
        if not os.path.exists(runs_dir):
            return []

        runs = []
        for filename in os.listdir(runs_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(runs_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        runs.append(data)
                except Exception:
                    continue

        runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return runs[:limit]


_obs_service = None

def get_observability_service() -> ObservabilityService:
    global _obs_service
    if _obs_service is None:
        _obs_service = ObservabilityService()
    return _obs_service
