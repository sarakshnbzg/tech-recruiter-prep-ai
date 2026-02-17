from __future__ import annotations

import json
from typing import Any


def build_extract_requirements_prompts(
    *,
    job_title: str,
    job_desc: str,
    max_items: int,
) -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) for extracting requirements from a JD.
    Pure function: no I/O, no model calls.
    """
    system_prompt = (
        "You extract structured hiring requirements from job descriptions. "
        "Return ONLY valid JSON. No markdown."
    )

    schema_hint: dict[str, Any] = {
        "requirements": [
            {"requirement": "string (short)", "keywords": ["string", "string"]}
        ]
    }

    user_prompt = f"""
Extract the top {max_items} recruiter-relevant requirements from this job description.

Job Title: {job_title}

Job Description:
\"\"\"{job_desc}\"\"\"

Rules:
- Output MUST be valid JSON only.
- Output MUST match this schema:
{json.dumps(schema_hint, indent=2)}
- Keep each "requirement" short (5–12 words).
- "keywords" should be 2–5 concrete terms that can be searched in a resume.
""".strip()

    return system_prompt, user_prompt
