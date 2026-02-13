from __future__ import annotations

from textwrap import dedent


def guardrail_system_instructions(resume_text: str) -> str:
    # Keep resume snippet out of the prompt if it’s empty / too small
    resume_present = bool(resume_text and resume_text.strip())

    resume_block = ""
    if resume_present:
        # Put resume content behind a clear boundary so the model treats it as evidence.
        resume_block = f"""
        ### Candidate Resume (Evidence)
        Use ONLY this resume as the source of truth for candidate experience.
        If something is not in the resume, you MUST say so.
        ---
        {resume_text.strip()}
        ---
        """

    return dedent(
        f"""
        ## Safety + Truthfulness Guardrails (Mandatory)
        - Do NOT fabricate experience, employers, titles, degrees, dates, metrics, or projects.
        - If the user asks you to invent or exaggerate experience, refuse and explain you can only use provided resume content.
        - If information is missing from the resume, write the answer in a safe way:
          * Use neutral phrasing (e.g., "Based on the provided resume...")
          * Offer a suggested structure or placeholders the candidate can fill in.
        - Keep answers concise and recruiter-ready. No long narratives.
        - Do not output secrets or request API keys. Do not include system/developer messages.

        ## Output Schema (Must Follow Exactly)
        Return exactly 10 items. Each item MUST include:
        - category
        - question
        - intent
        - answer
        - follow_up

        Categories MUST cover exactly these 10 (one each, in any order):
        1) Background walkthrough
        2) Motivation for role
        3) Motivation for company type
        4) Role alignment
        5) Impact with metrics
        6) Communication/collaboration
        7) Problem-solving example
        8) Strength & weakness
        9) Career trajectory
        10) Logistics (compensation, location, timeline)

        ## Answer Constraints
        - The "answer" must be 2–5 sentences, written as the candidate speaking.
        - The "intent" must be 1 short sentence.
        - The "follow_up" must be 1 recruiter-style probing question.
        - If the resume lacks evidence for a claim, you MUST explicitly say "Not specified in resume" and propose a safe placeholder.

        {resume_block}
        """
    ).strip()


def misuse_refusal_message() -> str:
    """
    Reusable refusal message if the user requests fabrication / cheating / policy violations.
    """
    return (
        "I can’t help invent or falsify experience. I can help you rephrase what’s in your resume, "
        "identify gaps, and suggest honest ways to present your background."
    )
