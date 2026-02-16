from __future__ import annotations

import streamlit as st

from src.core.pdf_extract import extract_text_from_pdf
from src.core.generate import generate_recruiter_prep
from src.core.validation import validate_user_inputs
from src.prompts.system_prompts import SYSTEM_PROMPTS

st.set_page_config(
    page_title="Tech Recruiter Prep AI",
    page_icon="🧠",
    layout="wide",
)

st.title("Tech Recruiter Prep AI")
st.caption(
    "Generate recruiter-style screening questions + concise, recruiter-ready answers grounded in your resume."
)

# -----------------------------
# Sidebar: Settings
# -----------------------------
with st.sidebar:
    st.header("Settings")

    model = st.selectbox(
        "Model",
        options=[
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ],
        index=4,
        help="Choose the OpenAI model used for generation.",
    )

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
        options=["Intern", "Junior", "Mid", "Senior", "Staff/Lead"],
        index=2,
    )

    company_type = st.selectbox(
        "Company Type",
        options=["Startup", "Enterprise"],
        index=0,
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
# Generate
# -----------------------------
st.divider()
generate_clicked = st.button(
    "Generate 10 Recruiter Q&As", type="primary", use_container_width=True
)

if generate_clicked:
    # Basic validations
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
        validate_user_inputs(
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

    # Extract resume text
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
        except Exception as e:
            status.update(label="Resume extraction failed.", state="error")
            st.exception(e)
            st.stop()

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

    # Render output
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
