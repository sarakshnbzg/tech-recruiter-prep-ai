from __future__ import annotations

import json
import re
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import matplotlib.pyplot as plt

from ...helpers.openai_client import chat_json


@dataclass(frozen=True)
class RequirementMatch:
    requirement: str
    keywords: list[str]
    strength: int  # 0=Missing, 1=Partial, 2=Strong
    evidence_snippet: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_requirements_from_jd(
    model: str,
    temperature: float,
    job_title: str,
    job_desc: str,
    max_items: int = 10,
) -> list[dict[str, Any]]:
    system = (
        "You extract structured hiring requirements from job descriptions. "
        "Return ONLY valid JSON. No markdown."
    )

    schema_hint = {
        "requirements": [
            {"requirement": "string (short)", "keywords": ["string", "string"]}
        ]
    }

    user = f"""
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

    resp = chat_json(
        model=model,
        system_prompt=system,
        user_prompt=user,
        temperature=temperature,
    )

    data = json.loads(resp.choices[0].message.content)
    reqs = data.get("requirements", [])
    if not isinstance(reqs, list):
        return []
    return reqs[:max_items]


def score_requirements_against_resume(
    requirements: list[dict[str, Any]],
    resume_text: str,
) -> list[RequirementMatch]:
    resume_norm = _normalize(resume_text)

    results: list[RequirementMatch] = []
    for r in requirements:
        req = str(r.get("requirement", "")).strip()
        kws = r.get("keywords", [])
        keywords = [str(k).strip() for k in kws if str(k).strip()]
        if not req or not keywords:
            continue

        hits: list[str] = []
        for k in keywords:
            k_norm = _normalize(k)
            pattern = (
                r"\b" + re.escape(k_norm) + r"\b"
                if " " not in k_norm
                else re.escape(k_norm)
            )
            if re.search(pattern, resume_norm):
                hits.append(k)

        strength = 2 if len(hits) >= 2 else 1 if len(hits) == 1 else 0
        snippet = (
            extract_evidence_snippet(resume_text, hits)
            if hits
            else "Not specified in resume"
        )

        results.append(
            RequirementMatch(
                requirement=req,
                keywords=keywords,
                strength=strength,
                evidence_snippet=snippet,
            )
        )

    return results


def extract_evidence_snippet(
    resume_text: str, hit_keywords: list[str], max_len: int = 180
) -> str:
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    hit_lower = [_normalize(k) for k in hit_keywords]

    for ln in lines:
        ln_norm = _normalize(ln)
        if any(k in ln_norm for k in hit_lower):
            return (ln[:max_len] + "…") if len(ln) > max_len else ln

    text = resume_text.strip().replace("\n", " ")
    if not text:
        return "Not specified in resume"
    return (text[:max_len] + "…") if len(text) > max_len else text


def render_alignment_heatmap_png(matches: list[RequirementMatch]) -> bytes:
    if not matches:
        fig = plt.figure()
        plt.text(0.1, 0.5, "No requirements to plot", fontsize=12)
        plt.axis("off")
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
        plt.close(fig)
        return buf.getvalue()

    labels = [m.requirement for m in matches]
    data = [[m.strength] for m in matches]  # Nx1 “heatmap”

    fig, ax = plt.subplots(figsize=(8, max(3, 0.45 * len(labels))))
    im = ax.imshow(data, aspect="auto")

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xticks([0])
    ax.set_xticklabels(["Alignment Strength"], fontsize=10)

    for i, m in enumerate(matches):
        text = (
            "Strong" if m.strength == 2 else "Partial" if m.strength == 1 else "Missing"
        )
        ax.text(0, i, f"  {text}", va="center")

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(["Missing", "Partial", "Strong"])

    ax.set_title("Resume ↔ Job Description Alignment Heatmap", fontsize=12, pad=10)

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=220)
    plt.close(fig)
    return buf.getvalue()
