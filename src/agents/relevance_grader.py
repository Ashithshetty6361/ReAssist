"""
Relevance Grader Agent - Grades retrieved papers for query relevance
Single Responsibility: Binary relevance scoring ONLY

Inspired by Adaptive-Rag's grading node, adapted for ReAssist's
multi-paper research pipeline. Uses cheap model (gpt-3.5-turbo)
since grading is a simple yes/no classification task.
"""

import os
from src.core.llm_provider import get_llm_client, get_grader_model, get_grader_provider

# Load prompt from YAML
def _load_prompt():
    import yaml
    prompts_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'prompts.yaml')
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['relevance_grader']


class RelevanceGrader:
    """
    Grades each retrieved paper's relevance to the original query.
    Papers scoring 'no' are filtered out before downstream processing.
    
    Returns:
        - papers: Only the relevant papers (grade == 'yes')
        - graded_papers: All papers with grade field added
        - relevant_count: Number of relevant papers
        - dropped_count: Number of irrelevant papers dropped
        - success: Boolean
    """
    
    required_inputs = ['papers', 'query']
    
    def __init__(self, model=None):
        """Always use cheap model — grading is a simple binary task"""
        self.model = model or get_grader_model()
        self.client = get_llm_client(get_grader_provider())
        self._prompts = _load_prompt()
    
    def run(self, input_data):
        papers = input_data.get('papers', [])
        query = input_data.get('query', '')
        
        if not papers:
            return {
                'papers': [],
                'graded_papers': [],
                'relevant_count': 0,
                'dropped_count': 0,
                'success': False,
                'error': 'No papers to grade'
            }
        
        graded = []
        for paper in papers:
            grade = self._grade_single(paper, query)
            paper_copy = paper.copy()
            paper_copy['relevance_grade'] = grade
            graded.append(paper_copy)
        
        relevant = [p for p in graded if p['relevance_grade'] == 'yes']
        dropped = [p for p in graded if p['relevance_grade'] != 'yes']
        
        return {
            'papers': relevant,
            'graded_papers': graded,
            'relevant_count': len(relevant),
            'dropped_count': len(dropped),
            'dropped_titles': [p.get('title', 'Unknown') for p in dropped],
            'success': True,
            'error': None
        }
    
    def _grade_single(self, paper, query):
        """Grade a single paper's relevance. Returns 'yes' or 'no'."""
        title = paper.get('title', 'Unknown')
        abstract = paper.get('abstract', paper.get('summary', ''))[:800]
        
        prompt = self._prompts['prompt'].format(
            query=query,
            title=title,
            abstract=abstract
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._prompts['system']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for grading
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip().lower()
            # Extract yes/no from response
            if 'yes' in answer:
                return 'yes'
            elif 'no' in answer:
                return 'no'
            return 'yes'  # Default to keeping paper
            
        except Exception:
            # On error, default to 'yes' to avoid dropping valid papers
            return 'yes'


def create_relevance_grader(model=None):
    """Factory function — always uses cheap model for grading"""
    return RelevanceGrader(model=model)
