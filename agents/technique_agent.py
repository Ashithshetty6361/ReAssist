"""
Technique Agent - Suggests alternative algorithmic approaches NOT used in papers
Single Responsibility: Alternative technique suggestion ONLY
"""

import os
from openai import OpenAI


class TechniqueAgent:
    """Agent responsible for suggesting alternative techniques NOT used in existing papers"""
    
    # Define required inputs for context slicing
    required_inputs = ['synthesis', 'ideas']
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Technique Agent
        
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
                - synthesis: Synthesis text from Synthesizer Agent
                - ideas: Ideas text from Idea Generator Agent
        
        Returns:
            Dictionary containing:
                - techniques: List of alternative techniques (3-5)
                - success: Boolean
                - error: Error message if failed
        """
        synthesis_text = input_data.get('synthesis', '')
        ideas_text = input_data.get('ideas', '')
        
        prompt = f"""Based on the research synthesis and proposed ideas, identify 3-5 alternative algorithmic approaches or methods that were NOT used in the existing papers but could be promising.

SYNTHESIS OF EXISTING WORK:
{synthesis_text[:800]}...

PROPOSED IDEAS:
{ideas_text[:800]}...

For each alternative technique:
1. Name the method/algorithm
2. Explain why it might be promising for this problem
3. Note if it combines multiple approaches

Focus ONLY on suggesting techniques. Do NOT provide difficulty levels, timelines, or implementation guidance.

List 3-5 alternative techniques:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying alternative algorithmic approaches from related domains that could be applied to research problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            techniques_text = response.choices[0].message.content.strip()
            
            return {
                'techniques': techniques_text,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'techniques': None,
                'success': False,
                'error': str(e)
            }


def create_technique_agent(model="gpt-3.5-turbo"):
    """Factory function to create technique agent"""
    return TechniqueAgent(model=model)
