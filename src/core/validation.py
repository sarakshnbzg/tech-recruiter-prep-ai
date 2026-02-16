# src/core/validation.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, List

# Keep these aligned with your project requirements
ALLOWED_COMPANY_TYPES = ("Startup", "Enterprise")
ALLOWED_LEVELS = (
    "Intern",
    "Junior",
    "Mid",
    "Senior",
    "Staff",
    "Principal",
    "Lead",
    "Manager",
    "Director",
)

# If you want to enforce the project’s allowed models strictly:
ALLOWED_MODELS = (
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
)

# Reasonable safety limits for a student project
MAX_TITLE_CHARS = 120
MAX_JD_CHARS = 12_000
MAX_RESUME_MB = 5  # max upload size for PDF (soft enforcement)


def _is_blank(s: Optional[str]) -> bool:
    return s is None or not str(s).strip()


def validate_user_inputs(
    job_title: str,
    job_description: str,
    candidate_level: str,
    company_type: str,
    model: str,
    temperature: float,
    resume_file,  # Streamlit UploadedFile or None
    *,
    allowed_models: Sequence[str] = ALLOWED_MODELS,
) -> List[str]:
    """
    Validate UI inputs before calling the model.
    Returns a list of human-readable error messages. Empty list => OK.
    """
    errors: List[str] = []

    # Required text fields
    if _is_blank(job_title):
        errors.append("Job Title is required.")
    elif len(job_title.strip()) > MAX_TITLE_CHARS:
        errors.append(f"Job Title is too long (max {MAX_TITLE_CHARS} characters).")

    if _is_blank(job_description):
        errors.append("Job Description is required.")
    elif len(job_description.strip()) > MAX_JD_CHARS:
        errors.append(f"Job Description is too long (max {MAX_JD_CHARS} characters).")

    # Dropdowns / enums
    if _is_blank(candidate_level):
        errors.append("Candidate Level is required.")
    elif candidate_level not in ALLOWED_LEVELS:
        errors.append(f"Candidate Level must be one of: {', '.join(ALLOWED_LEVELS)}.")

    if _is_blank(company_type):
        errors.append("Company Type is required.")
    elif company_type not in ALLOWED_COMPANY_TYPES:
        errors.append(
            f"Company Type must be one of: {', '.join(ALLOWED_COMPANY_TYPES)}."
        )

    # Model + temperature
    if _is_blank(model):
        errors.append("Model selection is required.")
    elif allowed_models and model not in allowed_models:
        errors.append(f"Model must be one of: {', '.join(allowed_models)}.")

    try:
        temp = float(temperature)
        if temp < 0.0 or temp > 2.0:
            errors.append("Temperature must be between 0.0 and 2.0.")
    except Exception:
        errors.append("Temperature must be a number.")

    # Resume upload (optional, but your RFC expects it)
    if resume_file is None:
        errors.append("Resume PDF upload is required.")
    else:
        # Basic file checks (Streamlit UploadedFile has .name and .size)
        name = getattr(resume_file, "name", "") or ""
        size = getattr(resume_file, "size", None)

        if not name.lower().endswith(".pdf"):
            errors.append("Resume must be a PDF file.")

        if isinstance(size, int):
            max_bytes = MAX_RESUME_MB * 1024 * 1024
            if size > max_bytes:
                errors.append(f"Resume PDF is too large (max {MAX_RESUME_MB} MB).")

    return errors
