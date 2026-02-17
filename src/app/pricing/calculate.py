from __future__ import annotations

from dataclasses import dataclass
from src.app.settings import ALLOWED_MODELS

MODEL_PRICING_PER_1M: dict[str, tuple[float, float]] = {
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-3.5-turbo": (0.50, 1.50),
}

# Safety check: no drift allowed
_missing_pricing = set(ALLOWED_MODELS) - set(MODEL_PRICING_PER_1M.keys())
if _missing_pricing:
    raise ValueError(
        f"Missing pricing for allowed models: {sorted(_missing_pricing)}"
    )


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
        raise ValueError(f"No pricing configured for model: {model}")

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
