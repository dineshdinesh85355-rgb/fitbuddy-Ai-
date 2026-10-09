from .config import get_settings
from .gemini_client import generate_text
from .gemini_generator import SYSTEM_INSTRUCTION


def demo_updated_plan(
    original_plan: str,
    feedback: str
) -> str:

    return f"""
FITBUDDY – UPDATED DEMO PLAN

Your feedback:
{feedback}


UPDATED GUIDANCE

Keep the original 7-day structure but make gradual
changes based on the feedback.

Suggested approach:

• Keep at least one recovery day.
• Increase activity gradually.
• Reduce intensity if the current plan feels too difficult.
• Add comfortable cardio if requested.
• Replace movements that cause discomfort.
• Prioritize sleep and recovery.

The complete original plan remains stored in the database.


SAFETY

Stop activity if you experience pain, dizziness,
faintness or unusual shortness of breath.
"""


def update_workout_plan(
    original_plan: str,
    feedback: str
) -> str:

    settings = get_settings()

    if not settings.gemini_api_key:

        return demo_updated_plan(
            original_plan,
            feedback
        )

    prompt = f"""
Here is the user's current FitBuddy workout plan:

----- CURRENT PLAN -----

{original_plan}

----- END CURRENT PLAN -----


User feedback:

{feedback}


Task:

Rewrite the complete 7-day plan.

Incorporate reasonable parts of the user's feedback.

Rules:

• Preserve at least one recovery/rest day.
• Make changes gradually.
• Do not add dangerous exercise challenges.
• Do not provide calorie restriction instructions.
• Do not provide medical treatment.
• Do not make medical diagnoses.
• Keep the plan practical.
• Return the complete revised 7-day plan.
• Include a short safety note.
"""

    try:

        return generate_text(
            prompt=prompt,
            model=settings.workout_model,
            system_instruction=SYSTEM_INSTRUCTION
        )

    except Exception:

        return demo_updated_plan(
            original_plan,
            feedback
        )