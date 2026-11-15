"""
================================================================================
RESUME BULLET 2 SHOWCASE: SELF-HEALING JSON PARSER
================================================================================
Resume Point:
  "Achieved a 28% token reduction against standard Chain-of-Thought (CoT) baselines
   and 99.2% schema compliance across multi-run stability tests."

WHAT TO SHOW IN AN INTERVIEW:
  1. Explain why LLMs often fail schema compliance: They emit markdown code blocks
     (```json ... ```), conversational preambles ("Sure, here is your JSON:"),
     or single-quoted Python dictionaries.
  2. Show the 4-stage progressive cleanup pipeline in `clean_llm_json`:
     - Stage 1: Direct JSON parsing
     - Stage 2: Stripping markdown backticks (```json and ```)
     - Stage 3: Substring regex isolation between first '{' and last '}'
     - Stage 4: Single quote to double quote normalization
  3. Show `safe_json_parse`: Graceful fallback to default schema dictionary.

ORIGINAL SOURCE FILE:
  - src/utils/json_parser.py
================================================================================
"""

import json
import re


def clean_llm_json(response: str) -> dict:
    """
    Robustly parse JSON from raw LLM responses.
    Handles markdown blocks, conversational preambles, and syntax flaws.
    """
    if not response or not isinstance(response, str):
        raise ValueError("Response must be non-empty string")

    # Attempt 1: Direct parsing
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Strip markdown code blocks (```json ... ```)
    cleaned = response
    cleaned = re.sub(r'```json\s*', '', cleaned)
    cleaned = re.sub(r'```\s*', '', cleaned)

    # Attempt 3: Extract text between the first '{' and last '}'
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace:last_brace + 1]

    # Attempt 4: Fix single quotes to double quotes
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            fixed = cleaned.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON after cleanup: {str(e)}")


if __name__ == "__main__":
    print("=" * 65)
    print("TESTING 4-STAGE SELF-HEALING JSON PARSER")
    print("=" * 65)

    # Common LLM output with conversational preamble and markdown fence:
    dirty_llm_output = """
    Certainly! Here is the JSON output you requested:
    ```json
    {
        'faithful': true,
        'confidence': 0.95,
        'summary': 'All synthesized claims are supported by paper abstracts.'
    }
    ```
    Hope this helps with your literature review!
    """

    print("Raw Dirty LLM Output:")
    print(dirty_llm_output.strip())

    cleaned_dict = clean_llm_json(dirty_llm_output)
    print("\n✓ Parsed & Cleaned Successfully by clean_llm_json():")
    print(" ", cleaned_dict)
    print("=" * 65)

