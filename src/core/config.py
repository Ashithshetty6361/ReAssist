"""
Configuration - Centralized constants
Eliminates magic numbers scattered across codebase
"""

import os as _os

# Search Settings
MAX_PAPERS = 7  # Maximum papers to retrieve per query
DEFAULT_PAPERS = 5  # Default if not specified

# Model Settings — provider-aware defaults
from src.core.llm_provider import get_default_model as _get_model, get_grader_model as _get_grader
DEFAULT_MODEL = _get_model()  # auto-detected from LLM_PROVIDER
AVAILABLE_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",  # AWS Bedrock
    "anthropic.claude-3-haiku-20240307-v1:0",    # AWS Bedrock
    "llama3.1:8b-instruct-q4_K_M",               # Ollama
    "phi3:mini",                                 # Ollama
    "mistralai/Mistral-7B-Instruct-v0.3",         # HuggingFace
]

# Agent Settings
MAX_CHUNK_TOKENS = 2000  # Token limit for text chunking
SUMMARIZER_MAX_TOKENS = 500  # Max output tokens for summaries
SYNTHESIZER_MAX_TOKENS = 1500  # Max output tokens for synthesis

# RAG Settings
RAG_TOP_K = 10  # Number of chunks to retrieve
RAG_CHUNK_SIZE = 500  # Tokens per chunk
EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

# Retrieval Quality (Adaptive-Rag inspired)
RELEVANCE_THRESHOLD = 3       # Minimum relevant papers to proceed without rewrite
MAX_QUERY_REWRITES = 2        # Max rewrite attempts before web search fallback
VERIFICATION_CONFIDENCE = 0.7 # Min confidence to consider synthesis faithful
GRADER_MODEL = _get_grader()  # auto-detected from LLM_PROVIDER

# Web Search Fallback
WEB_SEARCH_MAX_RESULTS = 5

# Evaluation Settings
BASELINE_MAX_TOKENS = 2000  # Max tokens for single-prompt baseline

# Cost Tracking (USD per 1K tokens)
PRICING = {
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
    'gpt-4o': {'input': 0.0025, 'output': 0.01},
    'anthropic.claude-3-5-sonnet-20240620-v1:0': {'input': 0.003, 'output': 0.015},
    'anthropic.claude-3-haiku-20240307-v1:0': {'input': 0.00025, 'output': 0.00125},
    'text-embedding-ada-002': 0.0001,
    'amazon.titan-embed-text-v2:0': 0.00002,
    'ollama-local': {'input': 0.0, 'output': 0.0},
}

# Storage Settings
STORAGE_BACKEND = _os.getenv("STORAGE_BACKEND", "local")
S3_BUCKET_NAME = _os.getenv("S3_BUCKET_NAME", "reassist-storage")

# Logging
LOG_DIR = "logs"
EVALUATION_DIR = "evaluation"
DATA_DIR = "data"
PROMPTS_FILE = "prompts.yaml"

# Base dir of the src package (for resolving relative paths)
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
    from src.core.llm_provider import get_provider
    errors = []
    warnings = []

    provider = get_provider()

    # OpenAI key is only required when using OpenAI as the LLM provider
    if provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key == "your_openai_api_key_here":
            errors.append(
                "OPENAI_API_KEY is missing or still set to placeholder value.\n"
                "  Fix: Add OPENAI_API_KEY=sk-... to your .env file\n"
                "  Or switch to free models: set LLM_PROVIDER=ollama in .env\n"
                "  Or switch to AWS: set LLM_PROVIDER=bedrock in .env"
            )
    elif provider == "bedrock":
        # Check AWS credentials
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not aws_key or not aws_secret or aws_key == "your_aws_access_key_id":
            warnings.append(
                "AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not set in .env. "
                "Bedrock will rely on AWS IAM role or ~/.aws/credentials."
            )
    elif provider == "huggingface":
        hf_key = os.getenv("HF_API_KEY")
        if not hf_key or hf_key == "your_huggingface_api_key_here":
            errors.append(
                "HF_API_KEY is missing when LLM_PROVIDER=huggingface.\n"
                "  Fix: Add HF_API_KEY=hf_... to your .env file\n"
                "  Get a free token at https://huggingface.co/settings/tokens"
            )

    # Tavily is optional (web search fallback)
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        warnings.append(
            "TAVILY_API_KEY not set. Web search fallback will be disabled.\n"
            "  Fix: Add TAVILY_API_KEY=tvly-... to your .env file (optional)"
        )

    if warnings:
        print("\n[WARNING] Configuration notice:")
        for w in warnings:
            print(f"  [!] {w}")

    if errors:
        raise EnvironmentError(
            "\n\nReAssist startup failed -- missing configuration:\n\n" +
            "\n".join(f"  [X] {e}" for e in errors) +
            "\n\nCopy .env.example to .env and fill in your keys.\n"
        )

    return True
