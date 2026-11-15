"""
================================================================================
RESUME BULLET 1 SHOWCASE: AGENT INTERFACE CONTRACT (run(dict) -> dict)
================================================================================
Resume Point:
  "Designed a deterministic 7-agent research synthesis pipeline with strict
   typed run(dict) -> dict interfaces and dynamic context slicing."

WHAT TO SHOW IN AN INTERVIEW:
  1. Show that every agent adheres to a unified protocol: `run(input_data: dict) -> dict`.
  2. Point out `required_inputs = ['synthesis']`: This is how the agent formally
     declares what it needs from the global state.
  3. Show the predictable return dictionary structure: `{'gaps': ..., 'success': True, 'error': None}`.

ORIGINAL SOURCE FILE:
  - src/agents/gap_finder_agent.py
  - src/agents/idea_generator_agent.py
================================================================================
"""

from typing import Dict, Any, List
from src.agents.gap_finder_agent import GapFinderAgent
from src.agents.idea_generator_agent import IdeaGeneratorAgent


def showcase_agent_contracts():
    """
    Demonstrates the strict typed contract across agents.
    Notice how each agent defines its required_inputs manifest!
    """
    # 1. Inspect GapFinderAgent contract
    gap_agent = GapFinderAgent()
    print("Agent Name        :", gap_agent.__class__.__name__)
    print("Required Inputs   :", gap_agent.required_inputs)  # -> ['synthesis']
    
    # 2. Inspect IdeaGeneratorAgent contract
    idea_agent = IdeaGeneratorAgent()
    print("\nAgent Name        :", idea_agent.__class__.__name__)
    print("Required Inputs   :", idea_agent.required_inputs)  # -> ['gaps', 'synthesis']
    
    # 3. Simulate calling the agent with a clean sliced dictionary:
    mock_input = {
        "synthesis": "Recent transformers suffer from O(N^2) memory complexity in long contexts."
    }
    print("\n[Input Passed to GapFinderAgent.run(dict)]:")
    print(mock_input)
    
    print("\n[Standardized Output Schema Expected]:")
    print({
        "gaps": "1. Memory bounds on edge devices...",
        "success": True,
        "error": None
    })


if __name__ == "__main__":
    showcase_agent_contracts()

