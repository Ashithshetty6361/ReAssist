"""
Fair Baseline - Structured Chain-of-Thought Single Prompt
Provides fair comparison by receiving same context as multi-agent
"""

import os
import time
from openai import OpenAI


class FairBaselineAgent:
    """
    Single structured prompt that performs all steps:
    - Summarize papers
    - Extract themes
    - Identify gaps  
    - Generate ideas
    - Suggest techniques
    
    Receives SAME papers/context as multi-agent for fair comparison
    """
    
    required_inputs = ['papers']
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Fair Baseline Agent
        
        Args:
            model: OpenAI model to use
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def run(self, input_data):
        """
        Standard agent interface: run(dict) -> dict
        
        Args:
            input_data: Dictionary containing:
                - papers: List of paper dicts (same as multi-agent receives)
        
        Returns:
            Dictionary containing:
                - baseline_output: Complete analysis text
                - success: Boolean
                - error: Error message if failed
                - latency_seconds: Execution time
        """
        papers = input_data.get('papers', [])
        
        if not papers:
            return {
                'baseline_output': None,
                'success': False,
                'error': 'No papers provided',
                'latency_seconds': 0
            }
        
        # Build paper context (same abstracts multi-agent receives)
        paper_context = self._format_papers(papers)
        
        # Structured CoT prompt with explicit steps
        prompt = f"""You are a research analyst. Analyze the following {len(papers)} research papers and provide a comprehensive analysis following these EXACT steps:

PAPERS:
{paper_context}

TASK - Complete ALL of the following steps:

**STEP 1: SUMMARIZE EACH PAPER**
For each paper, provide:
- Main contribution
- Methods used
- Key results
- Limitations

**STEP 2: EXTRACT THEMES**
Identify:
- Common methodologies across papers
- Shared problem domains
- Technical patterns
- Emerging trends

**STEP 3: IDENTIFY GAPS**  
Find:
- Missing research areas
- Limitations in current approaches
- Unexplored combinations
- Methodological weaknesses

**STEP 4: GENERATE IDEAS**
Propose 3-5 novel research ideas that:
- Address identified gaps
- Are technically feasible
- Have clear problem statements
- Explain expected impact

**STEP 5: SUGGEST TECHNIQUES**
Recommend 3-5 alternative techniques/algorithms NOT used in these papers that could be applied to this domain.

Provide a structured, comprehensive analysis. Be specific and actionable."""

        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert research analyst who provides comprehensive, structured analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500  # Allow comprehensive response
            )
            
            latency = time.time() - start_time
            output_text = response.choices[0].message.content.strip()
            
            return {
                'baseline_output': output_text,
                'success': True,
                'error': None,
                'latency_seconds': latency
            }
            
        except Exception as e:
            latency = time.time() - start_time
            return {
                'baseline_output': None,
                'success': False,
                'error': str(e),
                'latency_seconds': latency
            }
    
    def _format_papers(self, papers):
        """Format papers for prompt context"""
        formatted = []
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', 'Untitled')
            authors = paper.get('authors', ['Unknown'])
            year = paper.get('year', 'Unknown')
            abstract = paper.get('abstract', paper.get('summary', 'No abstract available'))
            
            # Use summary if available (from summarizer agent)
            if 'summary' in paper and paper['summary']:
                abstract = paper['summary']
            
            formatted.append(f"""
Paper {i}: {title}
Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}
Year: {year}
Content: {abstract[:800]}{'...' if len(abstract) > 800 else ''}
---""")
        
        return '\n'.join(formatted)


def create_fair_baseline_agent(model="gpt-3.5-turbo"):
    """Factory function to create Fair Baseline Agent"""
    return FairBaselineAgent(model=model)
