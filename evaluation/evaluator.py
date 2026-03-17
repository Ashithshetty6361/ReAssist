"""
Evaluator - Compares multi-agent pipeline vs CoT baseline
Single Responsibility: Evaluation and scoring ONLY
"""

import os
import csv
import json
import time
from datetime import datetime
from agents.cot_baseline_agent import create_cot_baseline_agent


class Evaluator:
    """
    Compares multi-agent pipeline output against CoT baseline.
    Uses human annotations if available, automated scoring as fallback.
    """

    def __init__(self, model="gpt-3.5-turbo",
                 annotations_path="evaluation/human_annotations.csv"):
        self.model = model
        self.annotations_path = annotations_path
        self._annotations = self._load_annotations()
        self.cot_agent = create_cot_baseline_agent(model=model)

    def _load_annotations(self) -> dict:
        """Load human annotation CSV if it exists"""
        annotations = {}
        if not os.path.exists(self.annotations_path):
            return annotations
        try:
            with open(self.annotations_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row['query'].lower().strip(), row['agent_type'])
                    annotations[key] = {
                        'coverage_score': float(row['coverage_score']),
                        'specificity_score': float(row['specificity_score']),
                        'actionability_score': float(row['actionability_score'])
                    }
            print(f"  ✓ Loaded {len(annotations)} human annotations")
        except Exception as e:
            print(f"  ⚠️  Could not load annotations: {e}")
        return annotations

    def _automated_score(self, output: dict) -> dict:
        """
        Automated structural scoring when no human annotation exists.
        Scores based on completeness of output fields.
        """
        # Coverage: are the key output fields populated?
        coverage = 0.0
        for field in ['papers', 'synthesis', 'gaps', 'ideas']:
            val = output.get(field)
            if val and val != {} and val != []:
                coverage += 2.5

        # Specificity: do ideas have concrete hypotheses?
        ideas = output.get('ideas', [])
        if isinstance(ideas, list) and len(ideas) > 0:
            with_detail = sum(
                1 for i in ideas
                if isinstance(i, dict) and (i.get('hypothesis') or i.get('title'))
            )
            specificity = round((with_detail / len(ideas)) * 10, 1)
        elif isinstance(ideas, dict) and ideas.get('ideas_text'):
            specificity = 6.0
        else:
            specificity = 0.0

        # Actionability: does guidance have concrete first steps?
        guidance = output.get('guidance', [])
        if isinstance(guidance, list) and len(guidance) > 0:
            complete = sum(
                1 for g in guidance
                if isinstance(g, dict) and g.get('first_concrete_step')
            )
            actionability = round((complete / len(guidance)) * 10, 1)
        elif isinstance(guidance, dict) and guidance.get('guidance_text'):
            actionability = 5.0
        else:
            actionability = 0.0

        return {
            'coverage_score': round(coverage, 1),
            'specificity_score': specificity,
            'actionability_score': actionability
        }

    def _score_output(self, output: dict, query: str, agent_type: str) -> dict:
        """Score an output using human annotations or automated fallback"""
        key = (query.lower().strip(), agent_type)

        if key in self._annotations:
            scores = self._annotations[key]
            source = "human_annotation"
        else:
            scores = self._automated_score(output)
            source = "automated"

        avg = round(
            (scores['coverage_score'] +
             scores['specificity_score'] +
             scores['actionability_score']) / 3, 2
        )

        return {
            **scores,
            'avg_score': avg,
            'source': source,
            'query': query,
            'agent_type': agent_type
        }

    def run_baseline_comparison(self, query: str, papers: list,
                                 multi_agent_results: dict) -> dict:
        """
        Run CoT baseline and compare against multi-agent results.
        This is the main method called from main.py.
        """
        print("  Running CoT baseline for comparison...")
        start = time.time()
        cot_result = self.cot_agent.run({'query': query})
        cot_latency = round(time.time() - start, 2)

        cot_output = {}
        if cot_result.get('success') and cot_result.get('output'):
            cot_output = cot_result['output']

        ma_scores = self._score_output(multi_agent_results, query, 'multi_agent')
        cot_scores = self._score_output(cot_output, query, 'cot_baseline')

        delta = round(ma_scores['avg_score'] - cot_scores['avg_score'], 2)

        if abs(delta) < 0.5:
            winner = "tie"
        elif delta > 0:
            winner = "multi_agent"
        else:
            winner = "cot_baseline"

        if delta > 2.0:
            recommendation = (
                "Use multi-agent — significant quality gain justifies the cost."
            )
        elif delta > 0.5:
            recommendation = (
                "Use router — multi-agent is better but marginal. "
                "Let the router decide per query."
            )
        else:
            recommendation = (
                "Use CoT — quality is equivalent at 4x lower cost and 4x faster."
            )

        comparison = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'multi_agent_scores': ma_scores,
            'cot_baseline_scores': cot_scores,
            'winner': winner,
            'quality_delta': delta,
            'recommendation': recommendation,
            'cot_latency_seconds': cot_latency,
            'annotation_source': ma_scores['source'],
            'papers_analyzed': len(papers)
        }

        self._save_report(comparison)
        self._print_comparison(comparison)
        return comparison

    def _save_report(self, comparison: dict) -> None:
        """Save comparison report as JSON"""
        os.makedirs("evaluation/results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"evaluation/results/comparison_{timestamp}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        print(f"  📊 Report saved: {filepath}")

    def _print_comparison(self, comparison: dict) -> None:
        """Print formatted comparison to console"""
        ma = comparison['multi_agent_scores']
        cot = comparison['cot_baseline_scores']
        print("\n" + "=" * 60)
        print("EVALUATION COMPARISON")
        print("=" * 60)
        print(f"{'Metric':<22} {'Multi-Agent':>10} {'CoT':>10}")
        print("-" * 44)
        for metric, label in [
            ('coverage_score', 'Coverage'),
            ('specificity_score', 'Specificity'),
            ('actionability_score', 'Actionability')
        ]:
            print(f"{label:<22} {ma[metric]:>10.1f} {cot[metric]:>10.1f}")
        print("-" * 44)
        print(f"{'Average':<22} {ma['avg_score']:>10.2f} {cot['avg_score']:>10.2f}")
        print(f"\nWinner       : {comparison['winner'].upper()}")
        print(f"Quality delta: {comparison['quality_delta']:+.2f}")
        print(f"Scored by    : {comparison['annotation_source']}")
        print(f"Recommend    : {comparison['recommendation']}")
        print("=" * 60)


def create_evaluator(model="gpt-3.5-turbo"):
    """Factory function — matches import in main.py"""
    return Evaluator(model=model)
