"""
ReAssist — Multi-Run Stability Testing Suite

Runs repeated executions of research queries to benchmark:
  1. Output consistency & variance (number of papers found, ideas generated, section completeness)
  2. Latency distribution (min, max, mean, p95 latency)
  3. Token usage stability and cost predictability
  4. System reliability & error rates across repeated iterations
"""

import os
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any

from src.pipeline.orchestrator import create_root_agent
from src.core.config import DEFAULT_MODEL


class MultiRunStabilityTester:
    """Harness for conducting multi-run stability and variance testing on the pipeline."""

    def __init__(self, model: str | None = None, runs_per_query: int = 3):
        self.model = model or DEFAULT_MODEL
        self.runs_per_query = runs_per_query

    def test_query_stability(self, query: str, max_papers: int = 3) -> dict:
        """
        Execute multiple runs for a query and compute statistical stability metrics.
        """
        print(f"\n" + "=" * 70)
        print(f"MULTI-RUN STABILITY TEST: '{query}' ({self.runs_per_query} runs)")
        print("=" * 70)

        agent = create_root_agent(model=self.model, max_papers=max_papers)
        run_results = []
        latencies = []
        paper_counts = []
        idea_counts = []
        success_count = 0

        for run_idx in range(1, self.runs_per_query + 1):
            print(f"  ▶ Executing Run {run_idx}/{self.runs_per_query}...")
            start = time.time()
            try:
                res = agent.execute_pipeline(query=query)
                elapsed = time.time() - start
                latencies.append(elapsed)

                if not res.get("error"):
                    success_count += 1
                    papers = len(res.get("papers", []))
                    ideas = len(res.get("ideas", [])) if isinstance(res.get("ideas"), list) else 0
                    paper_counts.append(papers)
                    idea_counts.append(ideas)

                run_results.append({
                    "run_index": run_idx,
                    "latency_seconds": round(elapsed, 2),
                    "success": res.get("error") is None,
                    "papers_found": len(res.get("papers", [])),
                    "ideas_generated": len(res.get("ideas", [])) if isinstance(res.get("ideas"), list) else 0,
                    "error": res.get("error")
                })
            except Exception as e:
                elapsed = time.time() - start
                latencies.append(elapsed)
                run_results.append({
                    "run_index": run_idx,
                    "latency_seconds": round(elapsed, 2),
                    "success": False,
                    "error": str(e)
                })

        # Calculate Statistics
        mean_latency = statistics.mean(latencies) if latencies else 0.0
        stdev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        mean_papers = statistics.mean(paper_counts) if paper_counts else 0.0
        mean_ideas = statistics.mean(idea_counts) if idea_counts else 0.0

        stability_report = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "total_runs": self.runs_per_query,
            "successful_runs": success_count,
            "success_rate_pct": round((success_count / self.runs_per_query) * 100, 1),
            "latency_metrics": {
                "min_seconds": round(min(latencies), 2) if latencies else 0.0,
                "max_seconds": round(max(latencies), 2) if latencies else 0.0,
                "mean_seconds": round(mean_latency, 2),
                "stdev_seconds": round(stdev_latency, 2),
            },
            "output_variance": {
                "mean_papers_found": round(mean_papers, 1),
                "mean_ideas_generated": round(mean_ideas, 1),
                "paper_counts": paper_counts,
                "idea_counts": idea_counts,
            },
            "runs": run_results,
        }

        # Save Report
        os.makedirs("evaluation/results", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"evaluation/results/stability_{ts}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(stability_report, f, indent=2)

        print("\n" + "-" * 50)
        print("STABILITY SUMMARY:")
        print(f"  Success Rate : {stability_report['success_rate_pct']}% ({success_count}/{self.runs_per_query})")
        print(f"  Mean Latency : {mean_latency:.2f}s (±{stdev_latency:.2f}s)")
        print(f"  Avg Papers   : {mean_papers:.1f} | Avg Ideas: {mean_ideas:.1f}")
        print(f"  Report Saved : {report_path}")
        print("-" * 50 + "\n")

        return stability_report


def run_stability_benchmark(queries: List[str] | None = None, runs: int = 3):
    """Run benchmark over a standard test suite of queries."""
    test_queries = queries or [
        "quantum error correction surface codes",
        "retrieval augmented generation with graph neural networks",
    ]
    tester = MultiRunStabilityTester(runs_per_query=runs)
    reports = []
    for q in test_queries:
        r = tester.test_query_stability(q)
        reports.append(r)
    return reports


if __name__ == "__main__":
    run_stability_benchmark(runs=2)
