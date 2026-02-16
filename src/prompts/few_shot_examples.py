# src/prompts/few_shot_examples.py
from __future__ import annotations

import json


def recruiter_prep_one_item_example() -> str:
    """
    Generic example that demonstrates schema + style.
    Keep it neutral (no real company names, no unverifiable claims).
    """
    example = {
        "questions": [
            {
                "category": "Background walkthrough",
                "question": "Can you walk me through your background and what led you to this role?",
                "intent": "Assess the candidate’s narrative, relevant experience, and communication clarity.",
                "answer": (
                    "I started in a role focused on data and analytics, then moved into building product features that "
                    "improved user workflows. Over time I took on more ownership across delivery, partnering closely "
                    "with engineering and stakeholders to ship measurable improvements. Based on the resume provided, "
                    "my strongest themes are execution, collaboration, and iterative problem-solving."
                ),
                "follow_up": "Which project best represents the kind of impact you want to have in this role?",
            }
        ]
    }
    return json.dumps(example, indent=2)
