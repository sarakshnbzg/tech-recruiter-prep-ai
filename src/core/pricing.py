# src/core/pricing.py
from __future__ import annotations

from dataclasses import dataclass

MODEL_PRICING_PER_1M: dict[str, tuple[float, float]] = {
    # flagship models
    "gpt-4.1": (2.00, 8.00),  # typical developer pricing
    "gpt-4o": (2.50, 10.00),  # typical developer pricing
    # mid / balanced models
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4o-mini": (0.15, 0.60),
    # smaller, cheaper
    "gpt-4.1-nano": (0.10, 0.40),
}


@dataclass(frozen=True)
class CostBreakdown:
    prompt_tokens: int
    completion_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float


def estimate_cost(
    model: str, prompt_tokens: int, completion_tokens: int
) -> CostBreakdown:
    if model not in MODEL_PRICING_PER_1M:
        # Unknown model => can’t price it safely
        return CostBreakdown(prompt_tokens, completion_tokens, 0.0, 0.0, 0.0)

    in_price, out_price = MODEL_PRICING_PER_1M[model]
    input_cost = (prompt_tokens / 1_000_000) * in_price
    output_cost = (completion_tokens / 1_000_000) * out_price
    return CostBreakdown(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        input_cost_usd=input_cost,
        output_cost_usd=output_cost,
        total_cost_usd=input_cost + output_cost,
    )
