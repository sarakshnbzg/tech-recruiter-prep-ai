from __future__ import annotations

import streamlit as st

from src.app.alignment.generate import (
    extract_requirements_from_jd,
    render_alignment_heatmap_png,
    score_requirements_against_resume,
)
from src.app.recruiter_prep.generate import generate_recruiter_prep
from src.helpers.pdf_extract import extract_text_from_pdf
from src.app.settings import (
    ALLOWED_MODELS,
    ALLOWED_LEVELS,
    ALLOWED_COMPANY_TYPES,
    ALIGNMENT_TEMPERATURE,
    ALIGNMENT_MAX_ITEMS,
)
from src.app.validation import validate_user_inputs_or_raise
from src.app.recruiter_prep.prompts.system_prompts import SYSTEM_PROMPTS

# -----------------------------
# Helpers
# -----------------------------
def validate_inputs_or_stop(
    *,
    job_title: str,
    job_description: str,
    level: str,
    company_type: str,
    model: str,
    temperature: float,
    resume_file,
) -> None:
    if not job_title.strip():
        st.error("Please enter a Job Title.")
        st.stop()

    if not job_description.strip():
        st.error("Please paste a Job Description.")
        st.stop()

    if resume_file is None:
        st.error("Please upload your resume PDF.")
        st.stop()

    try:
        validate_user_inputs_or_raise(
            job_title,
            job_description,
            level,
            company_type,
            model,
            temperature,
            resume_file,
        )
    except Exception as e:
        st.error(str(e))
        st.stop()


def get_resume_text_or_stop(resume_file) -> str:
    with st.status("Extracting resume text…", expanded=False) as status:
        try:
            resume_bytes = resume_file.read()
            resume_text = extract_text_from_pdf(resume_bytes)
            if not resume_text.strip():
                st.error(
                    "Could not extract text from the PDF. Please try a different PDF."
                )
                st.stop()
            status.update(label="Resume extracted.", state="complete")
            return resume_text
        except Exception as e:
            status.update(label="Resume extraction failed.", state="error")
            st.exception(e)
            st.stop()


def run_alignment(
    *, model: str, job_title: str, job_description: str, resume_text: str
) -> None:
    with st.status("Generating alignment heatmap…", expanded=True) as status:
        try:
            requirements = extract_requirements_from_jd(
                model=model,
                temperature=ALIGNMENT_TEMPERATURE,
                job_title=job_title,
                job_desc=job_description,
                max_items=ALIGNMENT_MAX_ITEMS,
            )
            matches = score_requirements_against_resume(requirements, resume_text)
            heatmap_png = render_alignment_heatmap_png(matches)
            status.update(label="Alignment done!", state="complete")
        except Exception as e:
            status.update(label="Alignment failed.", state="error")
            st.exception(e)
            st.stop()

    st.subheader("Resume ↔ Job Description Alignment")
    st.image(heatmap_png, use_container_width=True)

    rows = [
        {
            "Requirement": m.requirement,
            "Keywords": ", ".join(m.keywords),
            "Strength": (
                "Strong"
                if m.strength == 2
                else "Partial" if m.strength == 1 else "Missing"
            ),
            "Evidence": m.evidence_snippet,
        }
        for m in matches
    ]

    st.markdown("### Evidence table")
    st.dataframe(rows, width="stretch")


def run_generation(
    *,
    model: str,
    prompt_key: str,
    temperature: float,
    job_title: str,
    job_description: str,
    level: str,
    company_type: str,
    resume_text: str,
) -> None:
    with st.status("Generating recruiter Q&As…", expanded=True) as status:
        try:
            result = generate_recruiter_prep(
                model=model,
                system_prompt_key=prompt_key,
                temperature=temperature,
                job_title=job_title,
                job_desc=job_description,
                level=level,
                company_type=company_type,
                resume_text=resume_text,
            )
            status.update(label="Done!", state="complete")
        except Exception as e:
            status.update(label="Generation failed.", state="error")
            st.exception(e)
            st.stop()

    prep = result.output
    cost = result.cost

    st.subheader("Results")
    st.caption(
        f"Estimated API cost: ${cost.total_cost_usd:.6f} "
        f"(input ${cost.input_cost_usd:.6f} + output ${cost.output_cost_usd:.6f}) • "
        f"Tokens: prompt {cost.prompt_tokens}, completion {cost.completion_tokens}"
    )

    for i, item in enumerate(prep.questions, start=1):
        header = f"{i}. {item.category}: {item.question}"
        with st.expander(header, expanded=(i == 1)):
            st.markdown(f"**Intent:** {item.intent}")
            st.markdown(f"**Recruiter-ready answer:** {item.answer}")
            st.markdown(f"**Follow-up probe:** {item.follow_up}")


# -----------------------------
# Page
# -----------------------------
st.set_page_config(page_title="First Round Tech Recruiter Prep AI", page_icon="🧠", layout="wide")

# Blue buttons (override Streamlit defaults)
st.markdown(
    """
<style>
/* Primary button */
div.stButton > button[kind="primary"] {
  background-color: #2563EB !important;  /* Blue */
  border: 1px solid #1D4ED8 !important;
  color: white !important;
}
div.stButton > button[kind="primary"]:hover {
  background-color: #1D4ED8 !important;
  border-color: #1E40AF !important;
}
div.stButton > button[kind="primary"]:active {
  background-color: #1E40AF !important;
}

/* Secondary buttons */
div.stButton > button:not([kind="primary"]) {
  border: 1px solid #2563EB !important;
  color: #2563EB !important;
}
div.stButton > button:not([kind="primary"]):hover {
  background-color: rgba(37, 99, 235, 0.08) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Tech Recruiter Prep AI")
st.caption(
    "Generate recruiter-style screening questions + concise, recruiter-ready answers grounded in your resume."
)

# -----------------------------
# Sidebar: Mode + Settings
# -----------------------------
with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "Choose what to generate",
        options=["Recruiter Q&As", "Resume ↔ Job Description Alignment"],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()
    st.header("Settings")

    # Model is shared by both modes
    model = st.selectbox(
        "Model",
        options=list(ALLOWED_MODELS),
        index=0,
        help="Choose the OpenAI model used for the selected mode.",
    )

    if mode == "Recruiter Q&As":
        temperature = st.slider(
            "Creativity (temperature)",
            min_value=0.0,
            max_value=1.5,
            value=0.7,
            step=0.1,
            help="Higher = more creative variation. Lower = more consistent.",
        )

        prompt_key = st.selectbox(
            "System prompt strategy",
            options=list(SYSTEM_PROMPTS.keys()),
            index=0,
            help="Internal prompt variants for experimentation/evaluation.",
        )
    else:
        # Alignment settings shown as fixed values (not editable)
        st.subheader("Alignment Settings")
        st.markdown(
            f"- **Extraction temperature:** `{ALIGNMENT_TEMPERATURE}`\n"
            f"- **Max requirements extracted:** `{ALIGNMENT_MAX_ITEMS}`"
        )
        st.caption("These are fixed for stability and consistent results.")
        # Keep these defined so validation can still run without branching complexity
        temperature = ALIGNMENT_TEMPERATURE
        prompt_key = list(SYSTEM_PROMPTS.keys())[0]

    st.divider()
    st.markdown("**Security**")
    st.write("- Refuses fabrication of resume experience")
    st.write("- Basic input sanitization for misuse patterns")

# -----------------------------
# Main: Inputs
# -----------------------------
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("Job & Candidate Inputs")

    job_title = st.text_input(
        "Job Title", placeholder="e.g., AI Engineer / ML Engineer / Data Scientist"
    )

    level = st.selectbox(
        "Candidate Level",
        options=list(ALLOWED_LEVELS),
        index=2,
    )

    # Company Type as radio (single selection)
    company_type = st.radio(
        "Company Type",
        options=list(ALLOWED_COMPANY_TYPES),
        index=0,
        horizontal=True,
    )

    job_description = st.text_area(
        "Job Description",
        height=220,
        placeholder="Paste the job description here...",
    )

with col_right:
    st.subheader("Resume Upload")
    resume_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        accept_multiple_files=False,
        help="We extract text from your PDF and use it as the source of truth.",
    )

    with st.expander("Tips for best PDF extraction"):
        st.write("- Selectable text PDFs work best (not scanned images).")
        st.write(
            "- If text extraction fails, try exporting your resume as a new PDF from Google Docs/Word."
        )

# -----------------------------
# Action
# -----------------------------
st.divider()

primary_label = (
    "Generate 10 Recruiter Q&As"
    if mode == "Recruiter Q&As"
    else "Generate Resume ↔ Job Description Alignment Heatmap"
)
run_clicked = st.button(primary_label, type="primary", use_container_width=True)

if run_clicked:
    validate_inputs_or_stop(
        job_title=job_title,
        job_description=job_description,
        level=level,
        company_type=company_type,
        model=model,
        temperature=temperature,
        resume_file=resume_file,
    )

    resume_text = get_resume_text_or_stop(resume_file)

    if mode == "Resume ↔ Job Description Alignment":
        run_alignment(
            model=model,
            job_title=job_title,
            job_description=job_description,
            resume_text=resume_text,
        )
    else:
        run_generation(
            model=model,
            prompt_key=prompt_key,
            temperature=temperature,
            job_title=job_title,
            job_description=job_description,
            level=level,
            company_type=company_type,
            resume_text=resume_text,
        )
