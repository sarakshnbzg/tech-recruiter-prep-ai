from __future__ import annotations

from pydantic import BaseModel, Field, conlist


class QAItem(BaseModel):
    category: str = Field(
        ..., description="One of the required recruiter screening categories"
    )
    question: str
    intent: str
    answer: str
    follow_up: str


class RecruiterPrepOutput(BaseModel):
    questions: conlist(QAItem, min_length=10, max_length=10)  # exactly 10
