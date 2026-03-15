"""
Idea Generator Agent - Generates novel research ideas
Single Responsibility: Research idea generation ONLY
"""

import os
from openai import OpenAI


class IdeaGeneratorAgent:
    """Agent responsible for generating novel research ideas"""
    
    # Define required inputs for context slicing
    required_inputs = ['gaps', 'synthesis']
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Idea Generator Agent
        
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
                - gaps: Research gaps from Gap Finder Agent
                - synthesis: Synthesis text from Synthesizer Agent
        
        Returns:
            Dictionary containing:
                - ideas: Generated research ideas
                - idea_count: Number of ideas generated
                - success: Boolean
                - error: Error message if failed
        """
        gaps_text = input_data.get('gaps', '')
        synthesis_text = input_data.get('synthesis', '')
        
        if not gaps_text:
            return {
                'ideas': None,
                'idea_count': 0,
                'success': False,
                'error': 'No gaps provided'
            }
        
        prompt = f"""Based on the following research synthesis and identified gaps, generate 5 novel research ideas:

SYNTHESIS:
{synthesis_text[:1000]}...

IDENTIFIED GAPS:
{gaps_text}

For each research idea, provide:
1. **Idea Title**: Catchy, descriptive title
2. **Problem Statement**: What specific problem does it address?
3. **Proposed Approach**: How would you tackle it? What methods/techniques?
4. **Expected Impact**: What would success look like? Why does it matter?
5. **Novelty**: What makes this idea different from existing work?

Generate 5 concrete, actionable research ideas:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative research ideator who generates novel, feasible research ideas that address real gaps in the literature."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher temperature for creativity
                max_tokens=1500
            )
            
            ideas_text = response.choices[0].message.content.strip()
            
            return {
                'ideas': ideas_text,
                'idea_count': 5,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'ideas': None,
                'idea_count': 0,
                'success': False,
                'error': str(e)
            }


def create_idea_generator_agent(model="gpt-3.5-turbo"):
    """Factory function to create idea generator agent"""
    return IdeaGeneratorAgent(model=model)
