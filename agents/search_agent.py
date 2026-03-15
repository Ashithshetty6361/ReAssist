"""
Search Agent - Finds relevant research papers from arXiv and Semantic Scholar
Single Responsibility: Paper discovery and retrieval ONLY
"""

import arxiv
import requests
from config import MAX_PAPERS


class SearchAgent:
    """Agent responsible for searching and retrieving research papers"""
    
    # Define required inputs for context slicing
    required_inputs = ['query']
    
    def __init__(self, max_papers=MAX_PAPERS):
        """
        Initialize Search Agent
        
        Args:
            max_papers: Maximum number of papers to retrieve (from config)
        """
        self.max_papers = max_papers
    
    def run(self, input_data):
        """
        Standard agent interface: run(dict) -> dict
        
        Args:
            input_data: Dictionary containing:
                - query: Research topic or keywords
        
        Returns:
            Dictionary containing:
                - papers: List of paper dictionaries with metadata
                - count: Number of papers found
                - success: Boolean
                - error: Error message if failed
        """
        query = input_data.get('query', '')
        
        if not query:
            return {
                'papers': [],
                'count': 0,
                'success': False,
                'error': 'No query provided'
            }
        
        papers = []
        
        # Search arXiv
        try:
            arxiv_papers = self._search_arxiv(query)
            papers.extend(arxiv_papers)
        except Exception as e:
            pass  # Continue with Semantic Scholar
        
        # Search Semantic Scholar if needed
        if len(papers) < self.max_papers:
            try:
                semantic_papers = self._search_semantic_scholar(query, self.max_papers - len(papers))
                papers.extend(semantic_papers)
            except Exception:
                pass
        
        return {
            'papers': papers[:self.max_papers],
            'count': len(papers[:self.max_papers]),
            'success': True,
            'error': None
        }
    
    def _search_arxiv(self, query):
        """Search arXiv for papers"""
        papers = []
        
        search = arxiv.Search(
            query=query,
            max_results=self.max_papers,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        for result in search.results():
            paper = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'year': result.published.year if result.published else 'Unknown',
                'pdf_url': result.pdf_url,
                'source': 'arXiv',
                'arxiv_id': result.entry_id.split('/')[-1]
            }
            papers.append(paper)
        
        return papers
    
    def _search_semantic_scholar(self, query, limit=5):
        """Search Semantic Scholar for papers"""
        papers = []
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,authors,abstract,year,url,paperId'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('data', []):
                if not item.get('abstract'):
                    continue
                
                paper = {
                    'title': item.get('title', 'Unknown'),
                    'authors': [author.get('name', 'Unknown') for author in item.get('authors', [])],
                    'abstract': item.get('abstract', ''),
                    'year': item.get('year', 'Unknown'),
                    'pdf_url': item.get('url', ''),
                    'source': 'Semantic Scholar',
                    'semantic_id': item.get('paperId', '')
                }
                papers.append(paper)
        except Exception:
            pass
        
        return papers


def create_search_agent(max_papers=5):
    """Factory function to create search agent"""

    return SearchAgent(max_papers=max_papers)


