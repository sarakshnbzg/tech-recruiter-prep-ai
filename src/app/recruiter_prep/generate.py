from __future__ import annotations

import json
from dataclasses import dataclass

from src.helpers.openai_client import call_open_ai
from src.app.pricing.calculate import CostBreakdown, estimate_cost
from src.app.recruiter_prep.prompts.prompt_guardrails import guardrail_system_instructions
from src.app.recruiter_prep.prompts.system_prompts import SYSTEM_PROMPTS
from src.app.recruiter_prep.build_prompt import build_recruiter_prep_user_prompt
from src.app.recruiter_prep.schema import RecruiterPrepOutput


@dataclass(frozen=True)
class GenerationResult:
    output: RecruiterPrepOutput
    cost: CostBreakdown


def generate_recruiter_prep(
    *,
    model: str,
    system_prompt_key: str,
    temperature: float,
    job_title: str,
    job_desc: str,
    level: str,
    company_type: str,
    resume_text: str,
) -> GenerationResult:

    system_prompt = SYSTEM_PROMPTS.get(system_prompt_key)
    if not system_prompt:
        raise ValueError(f"Unknown system_prompt_key: {system_prompt_key}")

    use_few_shot = (system_prompt_key == "few_shot")

    user_prompt = build_recruiter_prep_user_prompt(
        job_title=job_title,
        job_desc=job_desc,
        level=level,
        company_type=company_type,
        resume_text=resume_text,
        use_few_shot=use_few_shot,
    )

    system_with_guardrails = f"{system_prompt}\n\n{guardrail_system_instructions()}"

    resp = call_open_ai(
        model=model,
        system_prompt=system_with_guardrails,
        user_prompt=user_prompt,
        temperature=temperature,
    )

    content = resp.choices[0].message.content
    data = json.loads(content)
    parsed = RecruiterPrepOutput.model_validate(data)

    prompt_tokens = getattr(resp.usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(resp.usage, "completion_tokens", 0) or 0
    cost = estimate_cost(model, prompt_tokens, completion_tokens)

    return GenerationResult(output=parsed, cost=cost)
