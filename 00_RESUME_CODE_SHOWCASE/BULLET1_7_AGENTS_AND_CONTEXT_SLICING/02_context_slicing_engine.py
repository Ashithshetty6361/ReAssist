"""
================================================================================
RESUME BULLET 1 SHOWCASE: DYNAMIC CONTEXT SLICING ENGINE
================================================================================
Resume Point:
  "Designed a deterministic 7-agent research synthesis pipeline with strict
   typed run(dict) -> dict interfaces and dynamic context slicing."

WHAT TO SHOW IN AN INTERVIEW:
  1. Open this file and show `slice_context(state, required_inputs)`.
  2. Explain the problem: Without slicing, Agent 7 receives all accumulated state
     (raw paper PDFs, preliminary search logs, etc.) causing O(N^2) token explosion.
  3. Explain the mechanism: `slice_context` checks the agent's `required_inputs`
     and extracts ONLY those keys, discarding all unnecessary context.
  4. Show `validate_agent_interface`: Ensures no agent can be registered into the
     pipeline without declaring its `required_inputs` manifest.

ORIGINAL SOURCE FILE:
  - src/utils/context_slicer.py
================================================================================
"""

from typing import Dict, Any, List


def slice_context(state: dict, required_inputs: list) -> dict:
    """
    Extract only required keys from state for agent input.
    
    Args:
        state: Full pipeline state dictionary (may contain 15,000+ tokens of raw papers)
        required_inputs: List of key names required by agent (e.g. ['synthesis'])
    
    Returns:
        Dictionary containing ONLY required keys
    
    Raises:
        KeyError: If required key is missing from state
    """
    sliced = {}
    for key in required_inputs:
        if key not in state:
            raise KeyError(
                f"Required input '{key}' not found in state. Available keys: {list(state.keys())}"
            )
        sliced[key] = state[key]
    return sliced


def validate_agent_interface(agent):
    """
    Validate that agent strictly adheres to the required_inputs manifest contract.
    """
    if not hasattr(agent, 'required_inputs'):
        raise AttributeError(f"{agent.__class__.__name__} missing 'required_inputs' attribute")
    if not isinstance(agent.required_inputs, list):
        raise TypeError(f"{agent.__class__.__name__}.required_inputs must be a list")


# ==============================================================================
# LIVE DEMONSTRATION OF CONTEXT SLICING IN ACTION
# ==============================================================================
if __name__ == "__main__":
    # Simulate a massive global state accumulating throughout the pipeline:
    global_pipeline_state = {
        "query": "Scaling Laws in Diffusion Models",
        "raw_paper_blobs": ["... 15,000 tokens of raw arXiv text ..."],
        "papers": [{"title": "Scaling Diffusion", "abstract": "..."}],
        "synthesis": "Diffusion models scale predictably with compute and dataset size.",
        "gaps": "Lack of high-resolution video benchmarks under compute limits.",
        "agent_timings": {"search": 1.2, "summarizer": 5.4}
    }
    
    print("=" * 70)
    print("GLOBAL PIPELINE STATE KEYS (Total accumulated state):")
    print(list(global_pipeline_state.keys()))
    print("=" * 70)
    
    # Gap Finder only needs 'synthesis'
    gap_finder_inputs = ['synthesis']
    sliced_for_gap_finder = slice_context(global_pipeline_state, gap_finder_inputs)
    print("\n[SLICED CONTEXT FOR GAP FINDER]:")
    print("  Keys passed:", list(sliced_for_gap_finder.keys()))
    print("  Tokens saved: Dropped 15,000 tokens of raw papers & search metadata!")
    
    # Idea Generator only needs 'gaps' and 'synthesis'
    idea_inputs = ['gaps', 'synthesis']
    sliced_for_idea_gen = slice_context(global_pipeline_state, idea_inputs)
    print("\n[SLICED CONTEXT FOR IDEA GENERATOR]:")
    print("  Keys passed:", list(sliced_for_idea_gen.keys()))
    print("=" * 70)

