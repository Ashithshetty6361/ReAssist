"""
ReAssist — Cost Projector

Given actual token counts from a free model run (Ollama / HuggingFace),
project what the cost would have been on paid models.

Usage:
    from src.utils.cost_projector import project_costs, PRICING

    # After a pipeline run, get token counts from TokenCounter
    projection = project_costs(
        input_tokens=12500,
        output_tokens=3200,
    )
    # Returns a dict with per-model cost estimates
"""

# ─── Pricing Table (USD per 1M tokens, as of mid-2025) ──────────────────────

PRICING = {
    # OpenAI
    "gpt-4o-mini": {
        "input": 0.15,     # $0.15 per 1M input tokens
        "output": 0.60,    # $0.60 per 1M output tokens
        "label": "GPT-4o Mini",
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
        "label": "GPT-4o",
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00,
        "label": "GPT-4 Turbo",
    },
    "gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50,
        "label": "GPT-3.5 Turbo",
    },
    # Anthropic
    "claude-3.5-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "label": "Claude 3.5 Sonnet",
    },
    "claude-3-haiku": {
        "input": 0.25,
        "output": 1.25,
        "label": "Claude 3 Haiku",
    },
    # Google
    "gemini-1.5-pro": {
        "input": 1.25,
        "output": 5.00,
        "label": "Gemini 1.5 Pro",
    },
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30,
        "label": "Gemini 1.5 Flash",
    },
    # Free / Local (for reference)
    "ollama-local": {
        "input": 0.0,
        "output": 0.0,
        "label": "Ollama (Local, Free)",
    },
}

# Default models to include in projections
DEFAULT_PROJECTION_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "claude-3.5-sonnet",
    "claude-3-haiku",
    "gemini-1.5-flash",
    "ollama-local",
]


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
) -> float:
    """
    Calculate the dollar cost for a specific model.

    Args:
        input_tokens: Number of input (prompt) tokens
        output_tokens: Number of output (completion) tokens
        model: Model name (must be a key in PRICING)

    Returns:
        Cost in USD
    """
    pricing = PRICING.get(model)
    if not pricing:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)


def project_costs(
    input_tokens: int,
    output_tokens: int,
    models: list[str] | None = None,
) -> dict:
    """
    Project costs across multiple paid models.

    Args:
        input_tokens: Total input tokens consumed in the pipeline run
        output_tokens: Total output tokens consumed in the pipeline run
        models: List of model names to project (defaults to DEFAULT_PROJECTION_MODELS)

    Returns:
        Dictionary with:
        - token_summary: {input_tokens, output_tokens, total_tokens}
        - projections: [{model, label, input_cost, output_cost, total_cost}]
        - cheapest_paid: The cheapest non-free model
        - most_expensive: The most expensive model
    """
    models = models or DEFAULT_PROJECTION_MODELS
    total_tokens = input_tokens + output_tokens

    projections = []
    for model_name in models:
        pricing = PRICING.get(model_name)
        if not pricing:
            continue

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        projections.append({
            "model": model_name,
            "label": pricing["label"],
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
        })

    # Sort by total cost descending
    projections.sort(key=lambda x: x["total_cost_usd"], reverse=True)

    # Find cheapest paid model
    paid = [p for p in projections if p["total_cost_usd"] > 0]
    cheapest_paid = paid[-1]["model"] if paid else None
    most_expensive = paid[0]["model"] if paid else None

    return {
        "token_summary": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "projections": projections,
        "cheapest_paid_model": cheapest_paid,
        "most_expensive_model": most_expensive,
    }


def format_projection_table(projection: dict) -> str:
    """Format a projection dict as a human-readable table string."""
    lines = [
        f"Token Summary: {projection['token_summary']['input_tokens']:,} input + "
        f"{projection['token_summary']['output_tokens']:,} output = "
        f"{projection['token_summary']['total_tokens']:,} total",
        "",
        f"{'Model':<25} {'Input Cost':>12} {'Output Cost':>12} {'Total Cost':>12}",
        "-" * 63,
    ]

    for p in projection["projections"]:
        lines.append(
            f"{p['label']:<25} ${p['input_cost_usd']:>10.6f} ${p['output_cost_usd']:>10.6f} ${p['total_cost_usd']:>10.6f}"
        )

    lines.append("-" * 63)
    if projection.get("cheapest_paid_model"):
        lines.append(f"Cheapest paid: {projection['cheapest_paid_model']}")
    if projection.get("most_expensive_model"):
        lines.append(f"Most expensive: {projection['most_expensive_model']}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Example: project costs for a typical multi-agent pipeline run
    result = project_costs(input_tokens=15000, output_tokens=4500)
    print(format_projection_table(result))
