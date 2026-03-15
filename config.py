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
