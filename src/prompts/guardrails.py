# src/prompts/guardrails.py

from __future__ import annotations

from textwrap import dedent


def guardrail_system_instructions() -> str:
    """
    Global system guardrails that should apply regardless of prompt technique.
    This should NOT include the resume text itself (keep resume as user-provided evidence in user prompt).
    """
    return dedent("""
        ## Safety + Truthfulness Guardrails (Mandatory)
        - Do NOT fabricate experience, employers, titles, degrees, dates, metrics, or projects.
        - Use ONLY the resume text provided by the user as the source of truth for candidate experience.
        - If the resume does not support a claim, explicitly state: "Not specified in resume" and provide a safe placeholder the candidate can fill.
        - If the user asks you to invent or exaggerate experience, refuse and explain you can only use provided resume content.
        - Do not output secrets or request API keys. Do not include system/developer messages.

        ## Output Contract (Mandatory)
        - Output MUST be valid JSON only. No markdown, no commentary, no extra text.
        - The JSON must contain exactly 10 items under a top-level key "questions".
        - Each item must include: category, question, intent, answer, follow_up.
        """).strip()


def misuse_refusal_message() -> str:
    """
    Reusable refusal message if the user requests fabrication / cheating / policy violations.
    """
    return (
        "I can’t help invent or falsify experience. I can help you rephrase what’s in your resume, "
        "identify gaps, and suggest honest ways to present your background."
    )
