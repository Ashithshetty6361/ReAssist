"""
ReAssist — Embedding Provider Abstraction

Supports multiple embedding backends:
  - "bedrock"     → Amazon Titan Embeddings via Bedrock (amazon.titan-embed-text-v2:0)
  - "openai"      → OpenAI text-embedding-ada-002 / text-embedding-3-small (paid)
  - "ollama"      → nomic-embed-text via Ollama (free, local)
  - "huggingface" → sentence-transformers via HuggingFace (free, local)

The provider is selected via EMBEDDING_PROVIDER env var.
Defaults to "ollama" for free local embeddings.
"""

import os
from functools import lru_cache


EMBEDDING_PROVIDERS = {
    "bedrock": {
        "model": "amazon.titan-embed-text-v2:0",
        "region": "us-east-1",
    },
    "openai": {
        "model": "text-embedding-ada-002",
    },
    "ollama": {
        "model": "nomic-embed-text",
        "base_url": "http://localhost:11434",
    },
    "huggingface": {
        "model": "BAAI/bge-large-en-v1.5",
    },
}


def get_embedding_provider() -> str:
    """Return the active embedding provider name."""
    val = os.getenv("EMBEDDING_PROVIDER", "ollama").lower().strip()
    if val in ("aws_bedrock", "bedrock_aws"):
        return "bedrock"
    return val


@lru_cache(maxsize=1)
def get_embeddings():
    """
    Return a LangChain Embeddings instance for the active provider.
    Cached so we only initialize once.
    """
    provider = get_embedding_provider()

    if provider == "bedrock":
        try:
            from langchain_community.embeddings import BedrockEmbeddings
            import boto3
        except ImportError:
            raise ImportError(
                "langchain-community and boto3 are required for Bedrock embeddings. "
                "Run: pip install langchain-community boto3"
            )
        region = os.getenv("AWS_REGION", EMBEDDING_PROVIDERS["bedrock"]["region"])
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
            aws_session_token=os.getenv("AWS_SESSION_TOKEN") or None,
        )
        return BedrockEmbeddings(
            client=client,
            model_id=EMBEDDING_PROVIDERS["bedrock"]["model"]
        )

    elif provider == "openai":
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-openai is required for OpenAI embeddings. "
                "Run: pip install langchain-openai"
            )
        return OpenAIEmbeddings(
            model=EMBEDDING_PROVIDERS["openai"]["model"],
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

    elif provider == "ollama":
        try:
            from langchain_community.embeddings import OllamaEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-community is required for Ollama embeddings. "
                "Run: pip install langchain-community"
            )
        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            EMBEDDING_PROVIDERS["ollama"]["base_url"]
        )
        # Normalize base_url: strip trailing slashes and OpenAI-compatible /v1 suffix
        base_url = base_url.rstrip("/").removesuffix("/v1")
        return OllamaEmbeddings(
            model=EMBEDDING_PROVIDERS["ollama"]["model"],
            base_url=base_url,
        )

    elif provider == "huggingface":
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-community and sentence-transformers are required "
                "for HuggingFace embeddings. "
                "Run: pip install langchain-community sentence-transformers"
            )
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_PROVIDERS["huggingface"]["model"],
        )

    else:
        raise ValueError(
            f"Unknown EMBEDDING_PROVIDER '{provider}'. "
            f"Supported: bedrock, openai, ollama, huggingface"
        )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of text strings into vectors."""
    embeddings = get_embeddings()
    return embeddings.embed_documents(texts)
