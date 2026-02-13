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
- 🧪 Internal prompt experimentation (5 techniques)

---

## 🏗 Architecture Overview

![Architecture Diagram](assets/Tech_Recruiter_Prep_AI_Architecture_Diagram.png)

```mermaid
flowchart TD
  U[User] --> S[Streamlit UI]
  U -->|Upload resume PDF| S
  U -->|Enter JD title + description| S
  U -->|Select level + company type| S
  U -->|Choose model + temperature| S

  S --> P[Resume text extraction]
  P --> B[Prompt builder\n5 system prompt variants]
  B --> O[OpenAI API call\nModel + temperature]
  O --> R[Response parser\n10 structured Q&A items]
  R --> S

  S --> E[UI rendering\nCollapsible Q&A sections]

  S --> G[Security guard\nNo fabrication policy]
  G --> S

