# src/settings.py
from __future__ import annotations

# -----------------------------
# UI / Domain enums
# -----------------------------
ALLOWED_COMPANY_TYPES = ("Startup", "Enterprise")

ALLOWED_LEVELS = (
    "Intern",
    "Junior",
    "Mid",
    "Senior",
    "Staff/Lead",   # keep consistent with Streamlit UI
)

ALLOWED_MODELS = (
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-3.5-turbo",
)

# -----------------------------
# Alignment Settings (fixed)
# -----------------------------
ALIGNMENT_TEMPERATURE = 0.2
ALIGNMENT_MAX_ITEMS = 10

# -----------------------------
# Validation limits
# -----------------------------
MAX_TITLE_CHARS = 120
MAX_JD_CHARS = 12_000
MAX_RESUME_MB = 5
