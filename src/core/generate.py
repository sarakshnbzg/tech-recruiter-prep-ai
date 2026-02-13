from __future__ import annotations

import json
from .openai_client import chat_json
from .schema import RecruiterPrepOutput
from src.prompts.guardrails import guardrail_system_instructions as prompt_guardrails


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
) -> str:
    schema_hint = {
        "questions": [
            {
                "category": "string (must match one of the required categories)",
                "question": "string",
                "intent": "string",
                "answer": "string (concise, recruiter-ready, based on resume evidence)",
                "follow_up": "string",
            }
        ]
    }

    return f"""
You will generate EXACTLY 10 technical recruiter screen Q&A items.

Inputs:
- Job Title: {job_title}
- Candidate Level: {level}
- Company Type: {company_type}
- Job Description: {job_desc}

Resume Text (source of truth):
\"\"\"{resume_text}\"\"\"

Required categories (use each exactly once, in this order):
{json.dumps(CATEGORIES, indent=2)}

Output rules:
- Output MUST be valid JSON only.
- Output MUST match this schema shape:
{json.dumps(schema_hint, indent=2)}
- "questions" must contain exactly 10 objects.
- Each "category" must be exactly one of the required categories.
- Keep answers concise and recruiter-ready (3–6 sentences).
""".strip()


def generate_recruiter_prep(
    model: str,
    system_prompt: str,
    temperature: float,
    job_title: str,
    job_desc: str,
    level: str,
    company_type: str,
    resume_text: str,
) -> RecruiterPrepOutput:
    user_prompt = build_user_prompt(job_title, job_desc, level, company_type, resume_text)
    system_with_guardrails = f"{system_prompt}\n\n{prompt_guardrails(resume_text)}"
    resp = chat_json(model=model, system_prompt=system_with_guardrails, user_prompt=user_prompt, temperature=temperature)
    content = resp.choices[0].message.content
    data = json.loads(content)
    return RecruiterPrepOutput.model_validate(data)
