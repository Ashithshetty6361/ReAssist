"""
ReAssist — LLM Provider Abstraction Layer

Provides a unified `get_llm_client()` that returns an OpenAI-compatible
client based on the LLM_PROVIDER environment variable.

Supported providers:
  - "openai"      → standard OpenAI SDK (requires OPENAI_API_KEY)
  - "bedrock"     → AWS Bedrock via boto3 / Converse API (requires AWS credentials)
  - "ollama"      → local Ollama server (OpenAI-compatible /v1 endpoint)
  - "huggingface" → HuggingFace Inference API (free tier, requires HF_API_KEY)
"""

import os
import json
from types import SimpleNamespace
from functools import lru_cache
from openai import OpenAI


# ─── Default Model Names per Provider ────────────────────────────────────────

PROVIDER_DEFAULTS = {
    "openai": {
        "model": "gpt-4o-mini",
        "base_url": None,  # uses SDK default
    },
    "bedrock": {
        "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "region": "us-east-1",
    },
    "ollama": {
        "model": "llama3.1:8b-instruct-q4_K_M",
        "base_url": "http://localhost:11434/v1",
    },
    "huggingface": {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "base_url": "https://api-inference.huggingface.co/v1",
    },
}

# Lightweight / cheap models used for grading, rewriting, verification
PROVIDER_GRADER_MODELS = {
    "openai": "gpt-4o-mini",
    "bedrock": "anthropic.claude-3-haiku-20240307-v1:0",
    "ollama": "phi3:mini",
    "huggingface": "microsoft/Phi-3-mini-4k-instruct",
}


# ─── AWS Bedrock Client Adapter ──────────────────────────────────────────────

class BedrockChatCompletions:
    """OpenAI-compatible wrapper around AWS Bedrock Converse API."""

    def __init__(self, bedrock_runtime_client):
        self.client = bedrock_runtime_client

    def create(self, model: str, messages: list[dict], temperature: float = 0.3,
               max_tokens: int = 2000, response_format: dict | None = None, **kwargs):
        system_prompts = []
        bedrock_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_prompts.append({"text": content})
            elif role in ("user", "assistant"):
                bedrock_messages.append({
                    "role": role,
                    "content": [{"text": content}]
                })

        params = {
            "modelId": model,
            "messages": bedrock_messages,
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens,
            }
        }
        if system_prompts:
            params["system"] = system_prompts

        # If JSON output is requested via response_format, append instruction if needed
        if response_format and response_format.get("type") == "json_object":
            if not any("json" in s.get("text", "").lower() for s in system_prompts):
                params.setdefault("system", []).append({"text": "Respond strictly with a valid JSON object."})

        response = self.client.converse(**params)

        output_message = response.get("output", {}).get("message", {})
        content_blocks = output_message.get("content", [])
        text_content = "".join(b.get("text", "") for b in content_blocks)

        usage_data = response.get("usage", {})
        input_tokens = usage_data.get("inputTokens", 0)
        output_tokens = usage_data.get("outputTokens", 0)

        # Return OpenAI-compatible response object
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        role="assistant",
                        content=text_content
                    ),
                    finish_reason=response.get("stopReason", "stop")
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens
            )
        )


class BedrockClientWrapper:
    """Wrapper that provides an OpenAI SDK-like client.chat.completions interface for Bedrock."""

    def __init__(self, region_name: str | None = None):
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for AWS Bedrock provider. Run: pip install boto3"
            )
        region = region_name or os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
            aws_session_token=os.getenv("AWS_SESSION_TOKEN") or None,
        )
        self.chat = SimpleNamespace(completions=BedrockChatCompletions(self.bedrock_runtime))


# ─── Provider Accessors ───────────────────────────────────────────────────────

def get_provider() -> str:
    """Return the active LLM provider name (lowercase)."""
    val = os.getenv("LLM_PROVIDER", "openai").lower().strip()
    if val in ("aws_bedrock", "bedrock_aws"):
        return "bedrock"
    return val


def get_grader_provider() -> str:
    """Return the provider specifically for the grader/router (defaults to LLM_PROVIDER)."""
    val = os.getenv("GRADER_PROVIDER", get_provider()).lower().strip()
    if val in ("aws_bedrock", "bedrock_aws"):
        return "bedrock"
    return val


def get_default_model(provider: str | None = None) -> str:
    """Return the default model name for the active provider."""
    provider = provider or get_provider()
    explicit = os.getenv("MODEL_NAME")
    if explicit and explicit not in ("gpt-3.5-turbo", "gpt-4o-mini"):
        return explicit
    return PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["openai"])["model"]


def get_grader_model(provider: str | None = None) -> str:
    """Return a fast/cheap model for grading and classification tasks."""
    provider = provider or get_grader_provider()
    explicit = os.getenv("GRADER_MODEL")
    if explicit:
        return explicit
    return PROVIDER_GRADER_MODELS.get(provider, PROVIDER_GRADER_MODELS["openai"])


@lru_cache(maxsize=4)
def get_llm_client(provider: str | None = None):
    """
    Return a cached OpenAI-compatible client for the given provider.

    Usage:
        from src.core.llm_provider import get_llm_client, get_default_model
        client = get_llm_client()
        model = get_default_model()
        response = client.chat.completions.create(model=model, messages=[...])
    """
    provider = provider or get_provider()
    config = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["openai"])

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise EnvironmentError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Set it in .env, switch to LLM_PROVIDER=bedrock for AWS, or switch to LLM_PROVIDER=ollama for free local models."
            )
        return OpenAI(api_key=api_key)

    elif provider == "bedrock":
        region = os.getenv("AWS_REGION", config.get("region", "us-east-1"))
        return BedrockClientWrapper(region_name=region)

    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", config["base_url"])
        return OpenAI(
            base_url=base_url,
            api_key="ollama",  # placeholder — Ollama ignores this
        )

    elif provider == "huggingface":
        api_key = os.getenv("HF_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "HF_API_KEY is required when LLM_PROVIDER=huggingface. "
                "Get a free token at https://huggingface.co/settings/tokens"
            )
        return OpenAI(
            base_url=config["base_url"],
            api_key=api_key,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            f"Supported: openai, bedrock, ollama, huggingface"
        )


def check_provider_health() -> dict:
    """
    Quick health check: try to run a minimal test completion from the active provider.
    Returns {"healthy": bool, "provider": str, "model": str, "error": str|None}
    """
    provider = get_provider()
    model = get_default_model(provider)
    try:
        client = get_llm_client(provider)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return {
            "healthy": True,
            "provider": provider,
            "model": model,
            "error": None,
        }
    except Exception as e:
        return {
            "healthy": False,
            "provider": provider,
            "model": model,
            "error": str(e),
        }
