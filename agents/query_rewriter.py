"""
Query Rewriter Agent - Rewrites vague queries for better retrieval
Single Responsibility: Query optimization ONLY

When the Relevance Grader finds too few relevant papers,
this agent rewrites the query to be more specific/broader
and triggers a Search retry.
"""

import os
from openai import OpenAI

# Load prompt from YAML
def _load_prompt():
    import yaml
    prompts_path = os.path.join(os.path.dirname(__file__), '..', 'prompts.yaml')
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['query_rewriter']


class QueryRewriter:
    """
    Rewrites a search query to improve retrieval quality.
    
    Returns:
        - rewritten_query: The improved query string
        - original_query: The original query for reference
        - success: Boolean
    """
    
    required_inputs = ['query']
    
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._prompts = _load_prompt()
    
    def run(self, input_data):
        query = input_data.get('query', '')
        
        if not query:
            return {
                'rewritten_query': '',
                'original_query': '',
                'success': False,
                'error': 'No query provided'
            }
        
        prompt = self._prompts['prompt'].format(query=query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._prompts['system']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            rewritten = response.choices[0].message.content.strip()
            
            # Strip quotes if the model wraps the output
            rewritten = rewritten.strip('"').strip("'")
            
            return {
                'rewritten_query': rewritten,
                'original_query': query,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'rewritten_query': query,  # Fallback to original
                'original_query': query,
                'success': False,
                'error': str(e)
            }


def create_query_rewriter(model="gpt-3.5-turbo"):
    """Factory function"""
    return QueryRewriter(model=model)
