import streamlit as st

st.set_page_config(
    page_title="Tech Recruiter Prep AI",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Tech Recruiter Prep AI")
st.caption("Generate recruiter-style screening questions + concise answers from a job description + your resume.")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "OpenAI Model",
        ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"],
        index=4,
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.2, 0.4, 0.1)
    st.divider()
    st.write("Model:", model)
    st.write("Temperature:", temperature)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Info")
    job_title = st.text_input("Job Title", placeholder="e.g., AI Engineer")
    candidate_level = st.selectbox("Candidate Level", ["Junior", "Mid", "Senior", "Staff/Lead"])
    company_type = st.selectbox("Company Type", ["Startup", "Enterprise"])
    job_description = st.text_area("Job Description", height=220, placeholder="Paste the job description here...")

with col2:
    st.subheader("Your Resume")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    st.info("Resume extraction will be added next. For now, we just capture the file.")

st.divider()
st.subheader("Output")

generate = st.button("Generate 10 Recruiter Q&A", type="primary")

if generate:
    missing = []
    if not job_title.strip():
        missing.append("Job Title")
    if not job_description.strip():
        missing.append("Job Description")
    if resume_file is None:
        missing.append("Resume PDF")

    if missing:
        st.error(f"Missing required inputs: {', '.join(missing)}")
        st.stop()

    st.success("UI inputs captured ✅ Next step: resume parsing + OpenAI call.")

    # Placeholder for next steps
    st.json({
        "job_title": job_title,
        "candidate_level": candidate_level,
        "company_type": company_type,
        "model": model,
        "temperature": temperature,
        "resume_filename": resume_file.name,
    })
