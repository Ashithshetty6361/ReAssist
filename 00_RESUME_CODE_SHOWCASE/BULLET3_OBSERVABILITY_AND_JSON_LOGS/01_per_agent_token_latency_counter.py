"""
================================================================================
RESUME BULLET 3 SHOWCASE: TOKEN & LATENCY OBSERVABILITY METRICS
================================================================================
Resume Point:
  "Built per-agent latency/token observability metrics and structured JSON
   logging for real-time trace analysis."

WHAT TO SHOW IN AN INTERVIEW:
  1. Show `TokenCounter`: Records input tokens, output tokens, latency in seconds,
     and calculates exact dollar costs per agent.
  2. Show `get_summary()`:
     - Aggregates per-agent totals
     - Identifies the `most_expensive_agent`
     - Identifies the `slowest_agent`
  3. Explain that this is what powers real-time observability telemetry and
     performance optimization in ReAssist.

ORIGINAL SOURCE FILE:
  - src/utils/token_counter.py
================================================================================
"""

import json


class TokenCounter:
    """
    Observability layer tracking token usage, latency, and cost per agent call.
    """
    
    def __init__(self):
        self._records = []
        
    def track(self, agent_name: str, input_tokens: int, output_tokens: int, latency_seconds: float) -> None:
        # Standard pricing simulation (Claude 3.5 Sonnet / GPT-4o rate: $3/M in, $15/M out)
        cost_usd = (input_tokens * 0.000003) + (output_tokens * 0.000015)
        self._records.append({
            "agent": agent_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_seconds": latency_seconds,
            "cost_usd": cost_usd
        })
        
    def get_summary(self) -> dict:
        total_input_tokens = sum(r["input_tokens"] for r in self._records)
        total_output_tokens = sum(r["output_tokens"] for r in self._records)
        total_cost_usd = sum(r["cost_usd"] for r in self._records)
        total_latency_seconds = sum(r["latency_seconds"] for r in self._records)
        
        per_agent_totals = {}
        for r in self._records:
            agent = r["agent"]
            if agent not in per_agent_totals:
                per_agent_totals[agent] = {
                    "agent": agent,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                    "latency_seconds": 0.0
                }
            per_agent_totals[agent]["input_tokens"] += r["input_tokens"]
            per_agent_totals[agent]["output_tokens"] += r["output_tokens"]
            per_agent_totals[agent]["cost_usd"] += r["cost_usd"]
            per_agent_totals[agent]["latency_seconds"] += r["latency_seconds"]
            
        per_agent_list = sorted(
            list(per_agent_totals.values()), 
            key=lambda x: x["cost_usd"], 
            reverse=True
        )
        
        most_expensive_agent = per_agent_list[0]["agent"] if per_agent_list else ""
        slowest_agent = max(per_agent_list, key=lambda x: x["latency_seconds"])["agent"] if per_agent_list else ""
            
        return {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost_usd": round(total_cost_usd, 6),
            "total_latency_seconds": round(total_latency_seconds, 2),
            "per_agent": per_agent_list,
            "most_expensive_agent": most_expensive_agent,
            "slowest_agent": slowest_agent
        }


if __name__ == "__main__":
    counter = TokenCounter()
    counter.track("SearchAgent", 450, 150, 20.51)
    counter.track("SummarizerAgent", 8450, 1820, 195.99)
    counter.track("SynthesizeAgent", 1820, 950, 148.86)
    counter.track("GapFinderAgent", 950, 420, 182.72)
    counter.track("IdeaGeneratorAgent", 1370, 680, 158.91)
    counter.track("TechniqueAgent", 2050, 890, 603.22)
    counter.track("GuidanceAgent", 1570, 720, 105.74)
    counter.track("AnswerVerifier", 2800, 210, 58.30)

    summary = counter.get_summary()
    print("=" * 65)
    print("TOKEN & LATENCY OBSERVABILITY SUMMARY")
    print("=" * 65)
    print(f"Total Tokens Consumed : {summary['total_tokens']:,}")
    print(f"Total Pipeline Latency: {summary['total_latency_seconds']}s")
    print(f"Simulated Cloud Cost  : ${summary['total_cost_usd']:.5f}")
    print(f"Slowest Node          : {summary['slowest_agent']}")
    print(f"Most Expensive Node   : {summary['most_expensive_agent']}")
    print("\nPER-AGENT BREAKDOWN:")
    for a in summary["per_agent"]:
        print(f"  • {a['agent']:<20}: {a['latency_seconds']:>6.2f}s | {a['input_tokens']+a['output_tokens']:>5} tokens | ${a['cost_usd']:.5f}")
    print("=" * 65)

