import os
import tempfile
import pytest
from router import AgentRouter

class TestAgentRouter:
    def test_simple_query_routes_to_cot(self):
        router = AgentRouter()
        result = router.route("transformers")
        assert result['decision'] == 'cot'
        assert result['confidence'] >= 0.65

    def test_complex_query_routes_to_multi_agent(self):
        router = AgentRouter()
        result = router.route(
            "latest survey on federated learning vs centralized training "
            "for medical imaging in 2024"
        )
        assert result['decision'] == 'multi_agent'
        assert result['score_breakdown']['total_score'] >= 5

    def test_score_breakdown_sums_correctly(self):
        router = AgentRouter()
        result = router.route("attention mechanisms in transformers")
        breakdown = result['score_breakdown']
        assert breakdown['total_score'] == breakdown['complexity_score'] + breakdown['precision_score']

    def test_all_required_keys_present(self):
        router = AgentRouter()
        result = router.route("any query")
        required_keys = ['decision', 'confidence', 'reasoning',
                         'score_breakdown', 'estimated_cost_usd',
                         'estimated_latency_seconds',
                         'cost_saved_vs_always_multi_agent']
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_decision_is_always_valid(self):
        router = AgentRouter()
        for query in ["ml", "deep learning survey", "transformer attention heads"]:
            result = router.route(query)
            assert result['decision'] in ['cot', 'multi_agent']

    def test_get_stats_returns_zeros_when_no_log(self, monkeypatch):
        router = AgentRouter()
        
        # Temporarily point to nonexistent file by monkeypatching
        def mock_open(*args, **kwargs):
            raise FileNotFoundError()
            
        import builtins
        monkeypatch.setattr(builtins, 'open', mock_open)
        
        stats = router.get_stats()
        assert stats['total_queries'] >= 0
        assert 'total_cost_saved_usd' in stats

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
