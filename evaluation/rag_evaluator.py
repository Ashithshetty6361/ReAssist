"""
RAG Evaluator - 3-way comparison: multi-agent vs CoT vs RAG
"""

import os
import json
from datetime import datetime


class RAGEvaluator:
    """
    Extends the base Evaluator to support 3-way comparison.
    Adds retrieval-specific metrics: precision@k and recall@k.
    """

    def evaluate_retrieval(self, retrieved_papers: list,
                           query: str) -> dict:
        """
        Score the quality of RAG retrieval.
        Uses relevance_score from ChromaDB cosine similarity.
        """
        if not retrieved_papers:
            return {
                'precision_at_k': 0.0,
                'avg_relevance_score': 0.0,
                'k': 0
            }

        scores = [p.get('relevance_score', 0) for p in retrieved_papers]
        relevant = [s for s in scores if s >= 0.7]

        return {
            'precision_at_k': round(len(relevant) / len(scores), 2),
            'avg_relevance_score': round(sum(scores) / len(scores), 3),
            'k': len(retrieved_papers),
            'relevant_count': len(relevant)
        }

    def compare_three_way(self,
                          query: str,
                          multi_agent_results: dict,
                          cot_results: dict,
                          rag_results: dict,
                          retrieved_papers: list) -> dict:
        """
        Run 3-way comparison and save report.
        """
        from evaluation.evaluator import Evaluator
        base_eval = Evaluator()

        ma_scores = base_eval._score_output(
            multi_agent_results, query, 'multi_agent'
        )
        cot_scores = base_eval._score_output(
            cot_results, query, 'cot_baseline'
        )
        rag_scores = base_eval._score_output(
            rag_results, query, 'rag'
        )
        retrieval_scores = self.evaluate_retrieval(retrieved_papers, query)

        scores = {
            'multi_agent': ma_scores['avg_score'],
            'cot': cot_scores['avg_score'],
            'rag': rag_scores['avg_score']
        }
        winner = max(scores, key=scores.get)

        comparison = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'multi_agent_scores': ma_scores,
            'cot_scores': cot_scores,
            'rag_scores': rag_scores,
            'retrieval_metrics': retrieval_scores,
            'winner': winner,
            'rankings': sorted(scores, key=scores.get, reverse=True),
            'score_summary': scores
        }

        os.makedirs("evaluation/results", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"evaluation/results/rag_comparison_{ts}.json"
        with open(path, 'w') as f:
            json.dump(comparison, f, indent=2)

        self._print_three_way(comparison)
        return comparison

    def _print_three_way(self, c: dict) -> None:
        print("\n" + "=" * 65)
        print("3-WAY EVALUATION: Multi-Agent vs CoT vs RAG")
        print("=" * 65)
        print(f"{'Metric':<22} {'Multi-Agent':>12} {'CoT':>8} {'RAG':>8}")
        print("-" * 52)
        for metric, label in [
            ('coverage_score', 'Coverage'),
            ('specificity_score', 'Specificity'),
            ('actionability_score', 'Actionability')
        ]:
            ma = c['multi_agent_scores'][metric]
            cot = c['cot_scores'][metric]
            rag = c['rag_scores'][metric]
            print(f"{label:<22} {ma:>12.1f} {cot:>8.1f} {rag:>8.1f}")
        print("-" * 52)
        ma_avg = c['multi_agent_scores']['avg_score']
        cot_avg = c['cot_scores']['avg_score']
        rag_avg = c['rag_scores']['avg_score']
        print(f"{'Average':<22} {ma_avg:>12.2f} {cot_avg:>8.2f} {rag_avg:>8.2f}")
        print(f"\nRetrieval precision@{c['retrieval_metrics']['k']}: "
              f"{c['retrieval_metrics']['precision_at_k']:.0%}")
        print(f"Winner: {c['winner'].upper()}")
        print(f"Rankings: {' > '.join(c['rankings'])}")
        print("=" * 65)


def create_rag_evaluator():
    return RAGEvaluator()
