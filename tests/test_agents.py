import os
import unittest.mock
import pytest

class TestSearchAgent:
    def test_search_agent_returns_correct_structure(self):
        from agents.search_agent import create_search_agent
        agent = create_search_agent(max_papers=2)
        
        # Mock the arxiv search to return fake papers
        with unittest.mock.patch('arxiv.Search') as mock_search:
            mock_result = unittest.mock.MagicMock()
            mock_result.title = "Test Paper"
            mock_result.authors = [unittest.mock.MagicMock(name="Author One")]
            mock_result.summary = "Test abstract"
            mock_result.published.year = 2024
            mock_result.pdf_url = "https://example.com/paper.pdf"
            mock_result.entry_id = "https://arxiv.org/abs/2024.12345"
            
            # The prompt requested exactly this mocked attribute assignment
            mock_search.return_value.results.return_value = [mock_result]
            
            # We also mock arxiv.Client if the agent uses the modern Client.results(search) pattern
            with unittest.mock.patch('arxiv.Client') as mock_client:
                mock_client.return_value.results.return_value = [mock_result]
                
                result = agent.run({'query': 'test query'})
                
                assert result['success'] == True
                assert len(result['papers']) >= 1
                assert 'title' in result['papers'][0]

    def test_search_agent_handles_empty_query(self):
        from agents.search_agent import create_search_agent
        agent = create_search_agent()
        result = agent.run({'query': ''})
        assert result['success'] == False
        assert result['error'] is not None

class TestCoTBaseline:
    def test_cot_baseline_handles_missing_api_key(self):
        import os
        from unittest.mock import patch
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fake-key'}):
            from agents.cot_baseline_agent import create_cot_baseline_agent
            agent = create_cot_baseline_agent()
            
            # Mock the OpenAI client to raise an exception
            with unittest.mock.patch.object(agent.client.chat.completions, 'create') as mock_create:
                mock_create.side_effect = Exception("Invalid API key")
                result = agent.run({'query': 'test'})
                
                assert result['success'] == False
                assert result['error'] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
