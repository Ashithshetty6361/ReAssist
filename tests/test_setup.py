"""
Setup verification tests for ReAssist core components and utilities.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def test_basic_import():
    """Test that core modules can be imported without errors."""
    from src.pipeline.orchestrator import create_root_agent
    from src.agents.search_agent import create_search_agent
    from src.agents.summarize_agent import create_summarizer_agent
    from src.agents.synthesize_agent import create_synthesizer_agent
    from src.agents.gap_finder_agent import create_gap_finder_agent
    from src.agents.idea_generator_agent import create_idea_generator_agent
    from src.agents.technique_agent import create_technique_agent
    from src.utils.logger import get_logger
    from src.utils.timer import Timer
    from src.utils.helpers import chunk_text, count_tokens
    
    assert create_root_agent is not None
    assert create_search_agent is not None


def test_api_key():
    """Test that provider configuration is valid."""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    assert provider in ["ollama", "openai", "bedrock", "huggingface"]


def test_utilities():
    """Test chunking and token counting utility functions."""
    from src.utils.helpers import chunk_text, count_tokens
    
    text = "This is a test. " * 100
    chunks = chunk_text(text, max_tokens=50)
    assert len(chunks) > 0
    
    tokens = count_tokens("Hello world")
    assert tokens > 0


def test_logger():
    """Test structured logging system."""
    from src.utils.logger import reset_logger
    
    logger = reset_logger()
    logger.log_query("Test query")
    logger.log_papers_found(5)
    summary = logger.get_log_summary()
    assert summary is not None
    assert summary.get("papers_found") == 5


if __name__ == "__main__":
    test_basic_import()
    test_api_key()
    test_utilities()
    test_logger()
    print("All setup tests passed successfully.")
