"""
Configuration - Centralized constants
Eliminates magic numbers scattered across codebase
"""

# Search Settings
MAX_PAPERS = 7  # Maximum papers to retrieve per query
DEFAULT_PAPERS = 5  # Default if not specified

# Model Settings
DEFAULT_MODEL = "gpt-3.5-turbo"
AVAILABLE_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo-preview"
]

# Agent Settings
MAX_CHUNK_TOKENS = 2000  # Token limit for text chunking
SUMMARIZER_MAX_TOKENS = 500  # Max output tokens for summaries
SYNTHESIZER_MAX_TOKENS = 1500  # Max output tokens for synthesis

# RAG Settings (if implemented)
RAG_TOP_K = 10  # Number of chunks to retrieve
RAG_CHUNK_SIZE = 500  # Tokens per chunk
EMBEDDING_MODEL = "text-embedding-ada-002"

# Retrieval Quality (Adaptive-Rag inspired)
RELEVANCE_THRESHOLD = 3       # Minimum relevant papers to proceed without rewrite
MAX_QUERY_REWRITES = 2        # Max rewrite attempts before web search fallback
VERIFICATION_CONFIDENCE = 0.7 # Min confidence to consider synthesis faithful
GRADER_MODEL = "gpt-3.5-turbo"  # Cheap model for yes/no grading

# Web Search Fallback
WEB_SEARCH_MAX_RESULTS = 5

# Evaluation Settings
BASELINE_MAX_TOKENS = 2000  # Max tokens for single-prompt baseline

# Cost Tracking (USD per 1K tokens)
PRICING = {
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
    'text-embedding-ada-002': 0.0001
}

# Logging
LOG_DIR = "logs"
EVALUATION_DIR = "evaluation"
DATA_DIR = "data"
PROMPTS_FILE = "prompts.yaml"

# Base dir of the src package (for resolving relative paths)
import os as _os
_SRC_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def load_prompts():
    """
    Load all LLM prompts from the centralized YAML file.
    Returns a dict keyed by agent name.
    """
    import yaml
    import os
    prompts_path = os.path.join(_SRC_DIR, 'config', PROMPTS_FILE)
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_environment():
    """
    Validate all required environment variables at startup.
    Call this once in main.py and streamlit_app.py before anything else.
    Raises EnvironmentError with a clear human-readable message if anything is missing.
    """
    import os
    errors = []
    warnings = []

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        errors.append(
            "OPENAI_API_KEY is missing or still set to placeholder value.\n"
            "  Fix: Add OPENAI_API_KEY=sk-... to your .env file"
        )

    # Tavily is optional (web search fallback)
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        warnings.append(
            "TAVILY_API_KEY not set. Web search fallback will be disabled.\n"
            "  Fix: Add TAVILY_API_KEY=tvly-... to your .env file (optional)"
        )

    if warnings:
        print("\n[WARNING] Optional configuration warnings:")
        for w in warnings:
            print(f"  [!] {w}")

    if errors:
        raise EnvironmentError(
            "\n\nReAssist startup failed -- missing configuration:\n\n" +
            "\n".join(f"  [X] {e}" for e in errors) +
            "\n\nCopy .env.example to .env and fill in your keys.\n"
        )

    return True
