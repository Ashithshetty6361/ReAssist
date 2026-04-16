import json

class TokenCounter:
    """
    Observability layer to track token usage and cost per agent call.
    
    Cost Structure for Claude 3.5 Sonnet:
    - Input cost: $3.00 per million tokens = $0.000003 per token
    - Output cost: $15.00 per million tokens = $0.000015 per token
    """
    
    def __init__(self):
        self._records = []
        
    def track(self, agent_name: str, input_tokens: int, output_tokens: int, latency_seconds: float) -> None:
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
        total_tokens = total_input_tokens + total_output_tokens
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
        
        most_expensive_agent = ""
        slowest_agent = ""
        
        if per_agent_list:
            most_expensive_agent = per_agent_list[0]["agent"]
            slowest_agent_data = max(per_agent_list, key=lambda x: x["latency_seconds"])
            slowest_agent = slowest_agent_data["agent"]
            
        return {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost_usd, 6),
            "total_latency_seconds": round(total_latency_seconds, 2),
            "per_agent": per_agent_list,
            "most_expensive_agent": most_expensive_agent,
            "slowest_agent": slowest_agent
        }
        
    def reset(self) -> None:
        self._records = []
        
    def to_json(self) -> str:
        return json.dumps(self.get_summary(), indent=2)

if __name__ == "__main__":
    # Internal testing
    counter = TokenCounter()
    counter.track("SearchEngine", 1000, 200, 1.5)
    counter.track("Summarizer", 5000, 1000, 5.2)
    counter.track("SearchEngine", 1200, 250, 1.8)
    
    print("--- TokenCounter Summary ---")
    print(counter.to_json())
    
    counter.reset()
    print("\n--- After Reset ---")
    print(counter.to_json())
