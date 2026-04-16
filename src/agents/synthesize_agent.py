"""
Synthesizer Agent - Combines knowledge across multiple papers
Single Responsibility: Cross-paper knowledge synthesis ONLY
"""

import os
from openai import OpenAI


class SynthesizerAgent:
    """Agent responsible for synthesizing knowledge across papers"""
    
    # Define required inputs for context slicing
    required_inputs = ['papers']
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Synthesizer Agent
        
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
                - papers: List of papers with summaries
        
        Returns:
            Dictionary containing:
                - synthesis: Synthesis text
                - paper_count: Number of papers analyzed
                - success: Boolean
                - error: Error message if failed
        """
        papers = input_data.get('papers', [])
        conversation_context = input_data.get('conversation_context')
        
        if not papers:
            return {
                'synthesis': None,
                'paper_count': 0,
                'success': False,
                'error': 'No papers provided'
            }
        
        # Build synthesis prompt with all paper summaries
        papers_text = self._format_papers_for_synthesis(papers)
        
        context_block = ""
        if conversation_context:
            context_block = f"\nPrevious conversation context (if any):\n{conversation_context}\n"
        
        prompt = f"""Analyze the following research papers and provide a comprehensive synthesis:

{papers_text}
{context_block}
Provide a synthesis that includes:
1. **Common Themes**: What themes or topics appear across multiple papers?
2. **Methodological Approaches**: What different methods/algorithms are used? How do they compare?
3. **Key Findings**: What are the most important findings across these papers?
4. **Contradictions/Disagreements**: Are there any conflicting findings or approaches?
5. **Evolution of Ideas**: How has thinking evolved in this area?

Format your response clearly with these section headings:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert research synthesizer who identifies patterns and connections across multiple research papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            synthesis_text = response.choices[0].message.content.strip()
            
            return {
                'synthesis': synthesis_text,
                'paper_count': len(papers),
                'papers_analyzed': [p['title'] for p in papers],
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'synthesis': None,
                'paper_count': len(papers),
                'success': False,
                'error': str(e)
            }
    
    def _format_papers_for_synthesis(self, papers):
        """Format papers for synthesis prompt"""
        formatted = []
        
        for idx, paper in enumerate(papers):
            authors = ", ".join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors += " et al."
            
            paper_text = f"""
Paper {idx+1}: {paper['title']}
Authors: {authors}
Year: {paper['year']}
Summary: {paper.get('summary', paper.get('abstract', ''))}
"""
            formatted.append(paper_text)
        
        return "\n---\n".join(formatted)


def create_synthesizer_agent(model="gpt-3.5-turbo"):
    """Factory function to create synthesizer agent"""
    return SynthesizerAgent(model=model)
