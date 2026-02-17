from __future__ import annotations

import json
from typing import Sequence

from src.app.recruiter_prep.prompts.few_shot_example import recruiter_prep_one_item_example

CATEGORIES: Sequence[str] = [
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

def build_recruiter_prep_user_prompt(
    *,
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
{json.dumps(list(CATEGORIES), indent=2)}
""".strip()
