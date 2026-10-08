"""
Answer Verifier Agent - Hallucination guard for synthesis output
Single Responsibility: Faithfulness verification ONLY

After the full pipeline runs, this agent checks whether the
synthesis and identified gaps are actually grounded in the
retrieved paper summaries. Flags unsupported claims.
"""

import os
import json
from src.core.llm_provider import get_llm_client, get_grader_model, get_grader_provider

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
    
    def __init__(self, model=None):
        self.model = model or get_grader_model()
        self.client = get_llm_client(get_grader_provider())
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._prompts['system'] + "\nRespond ONLY with a JSON object: {\"faithful\": true/false, \"confidence\": 0.0-1.0, \"unsupported_claims\": [], \"summary\": \"...\"}. No markdown, no explanation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for verification
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Robust JSON extraction
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                parsed = json.loads(content)
                return {
                    'faithful': parsed.get('faithful', True),
                    'confidence': parsed.get('confidence', 0.5),
                    'unsupported_claims': parsed.get('unsupported_claims', []),
                    'verification_summary': parsed.get('summary', ''),
                    'success': True,
                    'error': None
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, make a best-effort interpretation
                is_faithful = 'unfaithful' not in content.lower() and 'not faithful' not in content.lower()
                return {
                    'faithful': is_faithful,
                    'confidence': 0.5,
                    'unsupported_claims': [],
                    'verification_summary': content[:200],
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


def create_answer_verifier(model=None):
    """Factory function"""
    return AnswerVerifier(model=model)
