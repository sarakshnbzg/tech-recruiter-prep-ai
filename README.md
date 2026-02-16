# Tech Recruiter Prep AI

A single-page Streamlit application that generates structured first-round **technical recruiter screening questions** and concise, recruiter-ready answers using OpenAI.

This tool helps candidates prepare for the initial recruiter conversation by aligning responses to:
- Job Title
- Job Description
- Candidate Level
- Company Type (Startup / Enterprise)
- Uploaded Resume (PDF)

## Docs
- [RFC PDF](docs/RFC-001_Tech_Recruiter_Prep_AI_One_Page_Full.pdf)

---

## 🚀 Features

- 📄 Resume upload (PDF → raw text extraction)
- 🎯 10 structured recruiter-style questions
- 🧠 Tailored answers aligned to JD + resume
- 🎛 Creativity control (temperature tuning)
- 🤖 Configurable OpenAI model selection
- 🔒 Anti-fabrication security guard
- 🧪 Internal prompt experimentation (6 techniques)
- 📊 Resume ↔ Job Description Alignment Heatmap
- 💰 API Cost Transparency

---

## 🏗 Architecture Overview

![Architecture Diagram](assets/Tech_Recruiter_Prep_AI_Architecture_Diagram.png)

## ⚙️ Setup & Run

- Clone the repository
```bash
git clone https://github.com/sarakshnbzg/tech-recruiter-prep-ai.git
cd tech-recruiter-prep-ai
```

- Create a Python environment (choose one)
```bash
# Conda (recommended)
conda create -n trp-ai python=3.10 -y
conda activate trp-ai

# or venv
python -m venv .venv
source .venv/bin/activate
```

- Install dependencies
```bash
pip install -r requirements.txt
```

- Set your OpenAI API key (macOS / Linux)
```bash
export OPENAI_API_KEY="your_api_key_here"
# To persist this, add the export to ~/.zshrc or ~/.bashrc
```

- Run the application
```bash
streamlit run main.py
```