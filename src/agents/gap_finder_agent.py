"""
Gap Finder Agent - Identifies research gaps and missing areas
Single Responsibility: Research gap identification ONLY
"""

from src.core.llm_provider import get_llm_client, get_default_model


class GapFinderAgent:
    """Agent responsible for identifying research gaps"""
    
    # Define required inputs for context slicing
    required_inputs = ['synthesis']
    
    def __init__(self, model=None):
        """
        Initialize Gap Finder Agent
        
        Args:
            model: LLM model to use (auto-detected from provider if None)
        """
        self.model = model or get_default_model()
        self.client = get_llm_client()
    
    def run(self, input_data):
        """
        Standard agent interface: run(dict) -> dict
        
        Args:
            input_data: Dictionary containing:
                - synthesis: Synthesis text from Synthesizer Agent
        
        Returns:
            Dictionary containing:
                - gaps: Research gaps identified
                - success: Boolean
                - error: Error message if failed
        """
        synthesis_text = input_data.get('synthesis', '')
        
        if not synthesis_text:
            return {
                'gaps': None,
                'success': False,
                'error': 'No synthesis provided'
            }
        
        # Build prompt for gap finding
        prompt = f"""Based on the following research synthesis, identify research gaps and missing areas:

{synthesis_text}

Identify specific research gaps including:
1. **Unanswered Questions**: What important questions remain unanswered?
2. **Methodological Limitations**: What limitations exist in current approaches?
3. **Missing Datasets/Benchmarks**: What data or evaluation frameworks are needed?
4. **Unexplored Combinations**: What combinations of techniques haven't been tried?
5. **Practical Applications**: What real-world applications are underexplored?
6. **Theoretical Foundations**: What theoretical aspects need more work?

For each gap, explain:
- What is missing or insufficient
- Why it matters
- What challenges it presents

Provide a structured list of gaps:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert research analyst who identifies gaps and opportunities in research literature."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1200
            )
            
            gaps_text = response.choices[0].message.content.strip()
            
            return {
                'gaps': gaps_text,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'gaps': None,
                'success': False,
                'error': str(e)
            }


def create_gap_finder_agent(model=None):
    """Factory function to create gap finder agent"""
    return GapFinderAgent(model=model)
