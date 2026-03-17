"""
CoT Baseline Agent - Runs entire pipeline as single Chain-of-Thought prompt
Single Responsibility: Baseline comparison ONLY
"""

import os
import time
import json
from openai import OpenAI
from config import DEFAULT_MODEL


class CoTBaselineAgent:
    """
    Chain-of-Thought baseline agent.
    Runs the same research task as the 7-agent pipeline
    but in a single structured prompt for comparison.
    """

    required_inputs = ['query']

    def __init__(self, model=DEFAULT_MODEL):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, input_data: dict) -> dict:
        query = input_data.get('query', '')
        if not query:
            return {
                'success': False,
                'error': 'No query provided',
                'output': None,
                'latency_seconds': 0,
                'approach': 'cot_baseline'
            }

        start = time.time()
        try:
            result = self._run_cot_prompt(query)
            elapsed = round(time.time() - start, 2)
            return {
                'success': True,
                'error': None,
                'output': result,
                'query': query,
                'latency_seconds': elapsed,
                'approach': 'cot_baseline',
                'model': self.model
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': None,
                'latency_seconds': round(time.time() - start, 2),
                'approach': 'cot_baseline'
            }

    def _run_cot_prompt(self, query: str) -> dict:
        system_prompt = (
            "You are a rigorous research intelligence assistant. "
            "Think step by step through each stage carefully before moving on. "
            "Return your response as valid JSON only — no extra text, no markdown backticks."
        )

        user_prompt = f"""Research Query: {query}

Think through this carefully and return a JSON object with these exact keys:

{{
  "search": [
    {{"title": "paper title", "year": 2023, "one_line": "what this paper does"}}
  ],
  "synthesis": {{
    "dominant_themes": ["theme1", "theme2", "theme3"],
    "common_methodology": "what approach most papers share",
    "consensus_finding": "what the field broadly agrees on",
    "evolution": "how approaches have shifted over time"
  }},
  "gaps": {{
    "unstudied_populations": ["gap1", "gap2"],
    "missing_baselines": ["comparison1"],
    "assumed_not_tested": ["assumption1"],
    "scale_gaps": ["scale issue1"]
  }},
  "ideas": [
    {{
      "title": "research question as a title",
      "hypothesis": "specific testable claim",
      "gap_addressed": "which gap this targets",
      "novelty_justification": "why this has not been done before",
      "feasibility_note": "what makes this achievable"
    }}
  ],
  "techniques": [
    {{
      "idea_title": "which idea this is for",
      "suggested_technique": "algorithm or method name",
      "why_alternative": "why better than what the papers used",
      "implementation_complexity": "Low or Medium or High"
    }}
  ],
  "guidance": [
    {{
      "idea_title": "which idea this is for",
      "difficulty": "Beginner or Intermediate or Advanced or Expert",
      "estimated_months": "3-6 months",
      "required_skills": ["skill1", "skill2"],
      "first_concrete_step": "the single most important first action to take",
      "biggest_risk": "most likely cause of failure"
    }}
  ]
}}

Identify 5-7 relevant papers in search.
Generate exactly 4 research ideas.
Provide techniques and guidance for each idea."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "raw_output": raw,
                "parse_error": "Could not parse as JSON"
            }


def create_cot_baseline_agent(model=DEFAULT_MODEL):
    """Factory function to create CoT baseline agent"""
    return CoTBaselineAgent(model=model)
