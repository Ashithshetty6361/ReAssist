import os
import unittest
from unittest.mock import patch
from src.router.agent_router import AgentRouter, ModelTier, create_router

class TestAgentRouter(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter(provider="bedrock")

    def test_simple_query_routes_to_cot(self):
        result = self.router.route("transformers")
        self.assertEqual(result['decision'], 'cot')
        self.assertGreaterEqual(result['confidence'], 0.65)
        self.assertEqual(result['suggested_tier'], ModelTier.TIER_1_FAST.value)

    def test_complex_query_routes_to_multi_agent(self):
        result = self.router.route(
            "latest survey on federated learning vs centralized training "
            "for medical imaging in 2024"
        )
        self.assertEqual(result['decision'], 'multi_agent')
        self.assertGreaterEqual(result['score_breakdown']['total_score'], 5)
        self.assertEqual(result['suggested_tier'], ModelTier.TIER_3_FRONTIER.value)

    def test_score_breakdown_sums_correctly(self):
        result = self.router.route("attention mechanisms in transformers")
        breakdown = result['score_breakdown']
        self.assertEqual(
            breakdown['total_score'],
            breakdown['complexity_score'] + breakdown['precision_score']
        )

    def test_all_required_keys_present(self):
        result = self.router.route("any query")
        required_keys = [
            'decision', 'confidence', 'reasoning',
            'suggested_tier', 'tier_dispatch',
            'score_breakdown', 'estimated_cost_usd',
            'estimated_latency_seconds',
            'cost_saved_vs_always_multi_agent'
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_decision_is_always_valid(self):
        for query in ["ml", "deep learning survey", "transformer attention heads"]:
            result = self.router.route(query)
            self.assertIn(result['decision'], ['cot', 'multi_agent'])

    def test_dynamic_agent_model_assignment(self):
        # Grader gets Tier 1 fast model
        grader_model = self.router.get_model_for_agent("grader")
        self.assertEqual(grader_model, "anthropic.claude-3-haiku-20240307-v1:0")

        # Synthesizer gets Tier 3 frontier model on complex queries
        synth_model = self.router.get_model_for_agent("synthesizer", query_complexity=5)
        self.assertEqual(synth_model, "anthropic.claude-3-5-sonnet-20240620-v1:0")

    def test_get_stats_empty(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            stats = self.router.get_stats()
            self.assertGreaterEqual(stats['total_queries'], 0)
            self.assertIn('total_cost_saved_usd', stats)

if __name__ == "__main__":
    unittest.main()
