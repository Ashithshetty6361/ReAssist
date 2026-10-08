import os
import unittest
from unittest.mock import patch, MagicMock

class TestSearchAgent(unittest.TestCase):
    def test_search_agent_returns_correct_structure(self):
        from src.agents.search_agent import create_search_agent
        agent = create_search_agent(max_papers=2)
        
        # Mock the arxiv search to return fake papers
        with patch('arxiv.Search') as mock_search:
            mock_result = MagicMock()
            mock_result.title = "Test Paper"
            mock_result.authors = [MagicMock(name="Author One")]
            mock_result.summary = "Test abstract"
            mock_result.published.year = 2024
            mock_result.pdf_url = "https://example.com/paper.pdf"
            mock_result.entry_id = "https://arxiv.org/abs/2024.12345"
            
            mock_search.return_value.results.return_value = [mock_result]
            
            with patch('arxiv.Client') as mock_client:
                mock_client.return_value.results.return_value = [mock_result]
                
                result = agent.run({'query': 'test query'})
                
                self.assertTrue(result['success'])
                self.assertGreaterEqual(len(result['papers']), 1)
                self.assertIn('title', result['papers'][0])

    def test_search_agent_handles_empty_query(self):
        from src.agents.search_agent import create_search_agent
        agent = create_search_agent()
        result = agent.run({'query': ''})
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])

class TestCoTBaseline(unittest.TestCase):
    def test_cot_baseline_handles_missing_api_key(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fake-key', 'LLM_PROVIDER': 'openai'}):
            from src.agents.cot_baseline_agent import create_cot_baseline_agent
            with patch('src.core.llm_provider.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_client.chat.completions.create.side_effect = Exception("Invalid API key")
                mock_openai.return_value = mock_client
                agent = create_cot_baseline_agent()
                result = agent.run({'query': 'test'})
                self.assertFalse(result['success'])
                self.assertIsNotNone(result['error'])

if __name__ == "__main__":
    unittest.main()
