# src/core/generate.py

from __future__ import annotations

import json

from .openai_client import chat_json
from .schema import RecruiterPrepOutput
from src.prompts.system_prompts import SYSTEM_PROMPTS
from src.prompts.guardrails import guardrail_system_instructions
from src.prompts.few_shot_examples import recruiter_prep_one_item_example


CATEGORIES = [
    "Background walkthrough",
    "Motivation for role",
    "Motivation for company type",
    "Role alignment",
    "Impact with metrics",
    "Communication/collaboration",
    "Problem-solving example",
    "Strength & weakness",
    "Career trajectory",
    "Logistics (compensation, location, timeline)",
]


def build_user_prompt(
    job_title: str,
    job_desc: str,
    level: str,
    company_type: str,
    resume_text: str,
    use_few_shot: bool,
) -> str:
    
    example_block = ""
    if use_few_shot:
        example_block = f"""
Here is an example of the expected JSON format and tone (1 item only):

{recruiter_prep_one_item_example()}

Use the same format and style for your output.
"""

    return f"""{example_block}
You will generate EXACTLY 10 technical recruiter screen Q&A items.

## Context Inputs
- Job Title: {job_title}
- Candidate Level: {level}
- Company Type: {company_type}
- Job Description: {job_desc}

## Resume Evidence (source of truth)
\"\"\"{resume_text}\"\"\"

## Required categories
Use each category exactly once, in this exact order:
{json.dumps(CATEGORIES, indent=2)}

""".strip()


def generate_recruiter_prep(
    model: str,
    system_prompt_key: str,  # technique prompt chosen from system_prompts.py
    temperature: float,
    job_title: str,
    job_desc: str,
    level: str,
    company_type: str,
    resume_text: str,
) -> RecruiterPrepOutput:
    
    if system_prompt_key not in SYSTEM_PROMPTS:
        raise ValueError(f"Unknown system_prompt_key: {system_prompt_key}")
    
    use_few_shot = system_prompt_key == "few_shot"
    system_prompt = SYSTEM_PROMPTS[system_prompt_key]

    user_prompt = build_user_prompt(job_title, job_desc, level, company_type, resume_text, use_few_shot,)

    # Compose system: technique behavior + global guardrails
    system_with_guardrails = f"{system_prompt}\n\n{guardrail_system_instructions()}"

    resp = chat_json(
        model=model,
        system_prompt=system_with_guardrails,
        user_prompt=user_prompt,
        temperature=temperature,
    )

    content = resp.choices[0].message.content
    data = json.loads(content)
    return RecruiterPrepOutput.model_validate(data)
