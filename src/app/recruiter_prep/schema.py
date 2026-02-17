from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel


class QAItem(BaseModel):
    category: str
    question: str
    intent: str
    answer: str
    follow_up: str


class RecruiterPrepOutput(BaseModel):
    questions: list[QAItem]
