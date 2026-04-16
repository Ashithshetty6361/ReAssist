"""
Answer Verifier Agent - Hallucination guard for synthesis output
Single Responsibility: Faithfulness verification ONLY

After the full pipeline runs, this agent checks whether the
synthesis and identified gaps are actually grounded in the
retrieved paper summaries. Flags unsupported claims.
"""

import os
import json
from openai import OpenAI

# Load prompt from YAML
def _load_prompt():
    import yaml
    prompts_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'prompts.yaml')
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)['answer_verifier']


class AnswerVerifier:
    """
    Verifies whether the synthesis output is faithful to source papers.
    Does NOT block the response — adds a verification report instead.
    
    Returns:
        - faithful: Boolean — is the synthesis grounded in papers?
        - confidence: Float 0-1 — how confident is the verifier?
        - unsupported_claims: List of claims not backed by papers
        - verification_summary: Human-readable explanation
        - success: Boolean
    """
    
    required_inputs = ['synthesis', 'papers', 'gaps']
    
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._prompts = _load_prompt()
    
    def run(self, input_data):
        synthesis = input_data.get('synthesis', '')
        papers = input_data.get('papers', [])
        gaps = input_data.get('gaps', '')
        
        if not synthesis:
            return {
                'faithful': True,
                'confidence': 0.0,
                'unsupported_claims': [],
                'verification_summary': 'No synthesis to verify',
                'success': False,
                'error': 'No synthesis provided'
            }
        
        # Build paper summaries context
        paper_summaries = self._format_paper_summaries(papers)
        
        prompt = self._prompts['prompt'].format(
            paper_summaries=paper_summaries,
            synthesis=str(synthesis)[:2000],
            gaps=str(gaps)[:1000]
        )
        
        try:
            from src.models.agent_outputs import VerificationResult
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._prompts['system']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for verification
                response_format=VerificationResult
            )
            
            result = response.choices[0].message.parsed
            
            return {
                'faithful': result.faithful,
                'confidence': result.confidence,
                'unsupported_claims': result.unsupported_claims,
                'verification_summary': result.summary,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'faithful': True,  # Don't block on error
                'confidence': 0.0,
                'unsupported_claims': [],
                'verification_summary': f'Verification failed: {str(e)}',
                'success': False,
                'error': str(e)
            }
    
    def _format_paper_summaries(self, papers):
        """Format papers into a string of summaries for verification"""
        parts = []
        for i, paper in enumerate(papers):
            title = paper.get('title', 'Unknown')
            summary = paper.get('summary', paper.get('abstract', ''))[:500]
            parts.append(f"Paper {i+1}: {title}\nSummary: {summary}")
        return "\n---\n".join(parts) if parts else "No papers available"


def create_answer_verifier(model="gpt-3.5-turbo"):
    """Factory function"""
    return AnswerVerifier(model=model)
