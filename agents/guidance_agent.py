"""
Guidance Agent - Provides research guidance for pursuing ideas
Single Responsibility: Difficulty assessment, skills, and timeline estimation ONLY
"""

import os
from openai import OpenAI


class GuidanceAgent:
    """Agent responsible for providing practical research guidance"""
    
    # Define required_inputs for context slicing
    required_inputs = ['ideas', 'techniques']
    
    def __init__(self, model="gpt-3.5-turbo"):
        """
        Initialize Guidance Agent
        
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
                - ideas: Ideas text from Idea Generator Agent
                - techniques: Techniques text from Technique Agent
        
        Returns:
            Dictionary containing:
                - guidance: Structured guidance for each idea/technique
                - success: Boolean
                - error: Error message if failed
        """
        ideas_text = input_data.get('ideas', '')
        techniques_text = input_data.get('techniques', '')
        
        prompt = f"""Based on the proposed research ideas and alternative techniques, provide practical implementation guidance.

PROPOSED IDEAS:
{ideas_text[:1000]}...

ALTERNATIVE TECHNIQUES:
{techniques_text[:800]}...

For each major idea/technique, provide:

1. **Difficulty Level**: Beginner / Intermediate / Advanced / Expert
2. **Required Skills**: Specific technical skills needed (e.g., "PyTorch, graph neural networks, distributed training")
3. **Estimated Timeline**: Realistic time estimate (e.g., "2-3 months", "6-12 months")
4. **Key Challenges**: Main obstacles to expect
5. **Resources Needed**: Datasets, compute resources, tools, etc.

Be specific and realistic. Focus ONLY on providing guidance."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an experienced research advisor who provides practical, realistic guidance for implementing research projects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1200
            )
            
            guidance_text = response.choices[0].message.content.strip()
            
            return {
                'guidance': guidance_text,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'guidance': None,
                'success': False,
                'error': str(e)
            }


def create_guidance_agent(model="gpt-3.5-turbo"):
    """Factory function to create guidance agent"""
    return GuidanceAgent(model=model)
