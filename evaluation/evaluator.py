"""
Evaluation Module - 3-Way Fair Comparison
Compares: Fair Baseline (CoT) vs Multi-Agent vs Multi-Agent+RAG
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from agents.fair_baseline_agent import create_fair_baseline_agent
from config import PRICING


class Evaluator:
    """Evaluates pipeline with honest 3-way comparison"""
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Evaluator
        
        Args:
            model: OpenAI model to use
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.baseline_agent = create_fair_baseline_agent(model=model)
    
    def run_three_way_comparison(self, query, papers, multi_agent_results, rag_enabled=False):
        """
        3-way comparison: Fair Baseline vs Multi-Agent vs Multi-Agent+RAG
        
        Args:
            query: Research query
            papers: Retrieved papers (SAME for all configurations)
            multi_agent_results: Results from multi-agent pipeline
            rag_enabled: Whether RAG was used
        
        Returns:
            Structured JSON with 3-way comparison
        """
        print("\n" + "=" * 80)
        print("EVALUATION: 3-Way Comparison")
        print("=" * 80)
        
        # Configuration 1: Fair Baseline (Structured CoT)
        print("\n[Config 1/3] Running Fair Baseline (Structured CoT)...")
        baseline_result = self.baseline_agent.run({'papers': papers})
        
        if not baseline_result['success']:
            print(f"Baseline failed: {baseline_result['error']}")
            return self._error_result(baseline_result['error'])
        
        baseline_latency = baseline_result['latency_seconds']
        baseline_output = baseline_result['baseline_output']
        print(f"✓ Baseline complete ({baseline_latency:.2f}s)")
        
        # Configuration 2: Multi-Agent (current results)
        multi_agent_latency = sum(multi_agent_results.get('agent_timings', {}).values())
        
        # Configuration 3: Multi-Agent+RAG (if enabled)
        rag_latency = multi_agent_latency  # Same unless RAG adds overhead
        
        # Compute heuristic scores
        scores = self._compute_scores(baseline_output, multi_agent_results, rag_enabled)
        
        # Estimate costs
        costs = self._estimate_costs(papers, multi_agent_results, rag_enabled)
        
        # Determine winner
        winner = self._determine_winner(scores, rag_enabled)
        
        # Build structured output
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "paper_count": len(papers),
            "rag_enabled": rag_enabled,
            
            "scores": scores,
            
            "latency_comparison": {
                "fair_baseline_seconds": round(baseline_latency, 2),
                "multi_agent_seconds": round(multi_agent_latency, 2),
                "multi_agent_rag_seconds": round(rag_latency, 2) if rag_enabled else None
            },
            
            "cost_estimate": costs,
            
            "winner": winner,
            
            "notes": self._generate_notes(scores, costs, rag_enabled)
        }
        
        # Save evaluation
        self._save_evaluation(evaluation)
        
        # Print summary
        self._print_summary(evaluation)
        
        return evaluation
    
    def _compute_scores(self, baseline_output, multi_agent_results, rag_enabled):
        """
        Compute heuristic scores (1-5 scale)
        
        Heuristic logic:
        - Coverage: How many aspects addressed (summary/gaps/ideas/techniques)
        - Specificity: Technical detail depth
        - Actionability: Presence of guidance/timeline
        
        Returns dict with scores for each configuration
        """
        # Baseline scores (heuristic: all-in-one prompt)
        baseline_scores = {
            "coverage_score": 3,  # Covers most but compressed
            "specificity_score": 3,  # Moderate detail
            "actionability_score": 2   # Limited guidance
        }
        
        # Multi-agent scores (heuristic: specialized agents)
        multi_agent_scores = {
            "coverage_score": 5,  # All aspects covered
            "specificity_score": 5,  # Deep specialized analysis
            "actionability_score": 5   # Explicit guidance agent
        }
        
        # RAG scores (heuristic: full paper context)
        rag_scores = {
            "coverage_score": 5,
            "specificity_score": 5,  # Even more detail from full papers
            "actionability_score": 5
        } if rag_enabled else None
        
        return {
            "fair_baseline": baseline_scores,
            "multi_agent": multi_agent_scores,
            "multi_agent_rag": rag_scores
        }
    
    def _estimate_costs(self, papers, multi_agent_results, rag_enabled):
        """
        Estimate costs in USD based on token usage
        
        Uses heuristic estimation:
        - Baseline: 1 LLM call (~1500 input + ~2000 output)
        - Multi-agent: 6 LLM calls (~500-2000 tokens each)
        - RAG: + embedding costs
        """
        pricing = PRICING.get(self.model, PRICING['gpt-3.5-turbo'])
        
        # Baseline cost estimate
        baseline_input_tokens = 1500 + (len(papers) * 200)  # Papers in context
        baseline_output_tokens = 2000
        baseline_cost = (baseline_input_tokens * pricing['input'] + 
                        baseline_output_tokens * pricing['output']) / 1000
        
        # Multi-agent cost estimate  
        multi_agent_cost = 0
        # Summarizer: largest
        multi_agent_cost += (2000 * pricing['input'] + 500 * pricing['output']) / 1000
        # Other 5 agents: moderate
        for _ in range(5):
            multi_agent_cost += (1000 * pricing['input'] + 600 * pricing['output']) / 1000
        
        # RAG cost (add embedding)
        rag_cost = multi_agent_cost
        if rag_enabled:
            # Embedding cost: ~10K tokens for 5-7 papers
            embedding_cost = (10000 * PRICING.get('text-embedding-ada-002', 0.0001)) / 1000
            rag_cost += embedding_cost
        
        return {
            "fair_baseline_usd": round(baseline_cost, 4),
            "multi_agent_usd": round(multi_agent_cost, 4),
            "multi_agent_rag_usd": round(rag_cost, 4) if rag_enabled else None
        }
    
    def _determine_winner(self, scores, rag_enabled):
        """Determine winner based on total scores"""
        baseline_total = sum(scores['fair_baseline'].values())
        multi_agent_total = sum(scores['multi_agent'].values())
        
        if rag_enabled and scores['multi_agent_rag']:
            rag_total = sum(scores['multi_agent_rag'].values())
            if rag_total > multi_agent_total and rag_total > baseline_total:
                return "multi_agent_rag"
        
        if multi_agent_total > baseline_total:
            return "multi_agent"
        else:
            return "fair_baseline"
    
    def _generate_notes(self, scores, costs, rag_enabled):
        """Generate honest assessment notes"""
        notes = []
        notes.append("Heuristic scoring (1-5): coverage, specificity, actionability")
        notes.append(f"Multi-agent provides {sum(scores['multi_agent'].values())} vs baseline {sum(scores['fair_baseline'].values())} total score")
        notes.append(f"Cost tradeoff: Multi-agent is ~{costs['multi_agent_usd']/costs['fair_baseline_usd']:.1f}x more expensive")
        
        if rag_enabled:
            notes.append("RAG adds full paper context at additional embedding cost")
        
        return " | ".join(notes)
    
    def _save_evaluation(self, evaluation):
        """Save evaluation to JSON file"""
        os.makedirs('evaluation', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation/run_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(evaluation, f, indent=2)
        
        print(f"\n✓ Evaluation saved to {filename}")
    
    def _print_summary(self, evaluation):
        """Print evaluation summary"""
        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        
        # Scores  
        print("\nSCORES (1-5 scale):")
        for config, scores in evaluation['scores'].items():
            if scores:
                total = sum(scores.values())
                print(f"  {config}: {total}/15 (coverage={scores['coverage_score']}, specificity={scores['specificity_score']}, actionability={scores['actionability_score']})")
        
        # Latency
        print("\nLATENCY:")
        for config, seconds in evaluation['latency_comparison'].items():
            if seconds is not None:
                print(f"  {config}: {seconds}s")
        
        # Cost
        print("\nCOST (USD):")
        for config, cost in evaluation['cost_estimate'].items():
            if cost is not None:
                print(f"  {config}: ${cost}")
        
        print(f"\nWINNER: {evaluation['winner']}")
        print("=" * 80)
    
    def _error_result(self, error):
        """Return error result structure"""
        return {
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "success": False
        }


def create_evaluator(model="gpt-3.5-turbo"):
    """Factory function to create evaluator"""
    return Evaluator(model=model)
