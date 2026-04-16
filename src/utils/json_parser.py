"""
JSON Parsing Utilities - Robust LLM JSON handling
Handles common LLM output issues like markdown blocks and trailing text
"""

import json
import re


def clean_llm_json(response: str) -> dict:
    """
    Robustly parse JSON from LLM response
    Handles markdown code blocks, extra text, formatting issues
    
    Args:
        response: Raw LLM response string
    
    Returns:
        Parsed dictionary
    
    Raises:
        ValueError: If JSON cannot be parsed after cleanup attempts
    """
    if not response or not isinstance(response, str):
        raise ValueError("Response must be non-empty string")
    
    # Try direct parsing first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Attempt 1: Remove markdown code blocks
    cleaned = response
    
    # Remove ```json ... ``` blocks
    cleaned = re.sub(r'```json\s*', '', cleaned)
    cleaned = re.sub(r'```\s*', '', cleaned)
    
    # Attempt 2: Extract text between first { and last }
    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace:last_brace + 1]
    
    # Attempt 3: Try parsing cleaned version
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Attempt 4: Try fixing common issues
        # Replace single quotes with double quotes (common LLM mistake)
        try:
            fixed = cleaned.replace("'", '"')
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        # If all attempts fail, raise with helpful message
        raise ValueError(f"Could not parse JSON after cleanup. Original error: {str(e)}. Cleaned text: {cleaned[:200]}...")


def safe_json_parse(response: str, default: dict = None) -> dict:
    """
    Parse JSON with fallback to default
    
    Args:
        response: LLM response
        default: Default dict to return on failure
    
    Returns:
        Parsed dict or default
    """
    try:
        return clean_llm_json(response)
    except (ValueError, json.JSONDecodeError) as e:
        if default is not None:
            return default
        raise
