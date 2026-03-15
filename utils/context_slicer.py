"""
Context Slicing Helper - Ensures strict context passing between agents
Prevents state accumulation and enforces agent interface contracts
"""


def slice_context(state: dict, required_inputs: list) -> dict:
    """
    Extract only required keys from state for agent input
    
    Args:
        state: Full pipeline state dictionary
        required_inputs: List of key names required by agent
    
    Returns:
        Dictionary containing only required keys
    
    Raises:
        KeyError: If required key is missing from state
    """
    sliced = {}
    
    for key in required_inputs:
        if key not in state:
            raise KeyError(f"Required input '{key}' not found in state. Available keys: {list(state.keys())}")
        sliced[key] = state[key]
    
    return sliced


def validate_agent_interface(agent):
    """
    Validate that agent has required_inputs attribute
    
    Args:
        agent: Agent instance to validate
    
    Raises:
        AttributeError: If agent doesn't have required_inputs
    """
    if not hasattr(agent, 'required_inputs'):
        raise AttributeError(f"{agent.__class__.__name__} missing 'required_inputs' attribute")
    
    if not isinstance(agent.required_inputs, list):
        raise TypeError(f"{agent.__class__.__name__}.required_inputs must be a list")
