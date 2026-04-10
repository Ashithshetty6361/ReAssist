"""
Web Search Agent - Tavily web search fallback
Single Responsibility: Live web search ONLY

When both Search Agent + Query Rewriter fail to find enough
relevant papers, this agent falls back to real-time web search
using the Tavily API. Results are formatted as paper-like dicts
for pipeline compatibility.
"""

import os


class WebSearchAgent:
    """
    Searches the web using Tavily API as a last-resort fallback.
    Returns results formatted as paper-like dicts for pipeline compatibility.
    
    Returns:
        - papers: List of web-result dicts (same schema as SearchAgent)
        - count: Number of results
        - source: 'web_search'
        - success: Boolean
    """
    
    required_inputs = ['query']
    
    def __init__(self, max_results=5):
        self.max_results = max_results
        self.api_key = os.getenv("TAVILY_API_KEY")
    
    def run(self, input_data):
        query = input_data.get('query', '')
        
        if not query:
            return {
                'papers': [],
                'count': 0,
                'source': 'web_search',
                'success': False,
                'error': 'No query provided'
            }
        
        if not self.api_key:
            return {
                'papers': [],
                'count': 0,
                'source': 'web_search',
                'success': False,
                'error': 'TAVILY_API_KEY not set. Web search fallback unavailable.'
            }
        
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.api_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=self.max_results,
                include_answer=False
            )
            
            papers = []
            for result in response.get('results', []):
                paper = {
                    'title': result.get('title', 'Web Result'),
                    'abstract': result.get('content', ''),
                    'authors': [],
                    'year': 'Unknown',
                    'pdf_url': result.get('url', ''),
                    'source': 'Web Search (Tavily)',
                    'relevance_score': result.get('score', 0.0)
                }
                papers.append(paper)
            
            return {
                'papers': papers,
                'count': len(papers),
                'source': 'web_search',
                'success': len(papers) > 0,
                'error': None if papers else 'No web results found'
            }
            
        except ImportError:
            return {
                'papers': [],
                'count': 0,
                'source': 'web_search',
                'success': False,
                'error': 'tavily-python not installed. Run: pip install tavily-python'
            }
        except Exception as e:
            return {
                'papers': [],
                'count': 0,
                'source': 'web_search',
                'success': False,
                'error': str(e)
            }


def create_web_search_agent(max_results=5):
    """Factory function"""
    return WebSearchAgent(max_results=max_results)
