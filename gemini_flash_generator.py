from .config import get_settings
from .gemini_client import generate_text


SYSTEM_INSTRUCTION = """
You are FitBuddy, a general wellness assistant.

Provide concise and practical nutrition or recovery guidance.

Do not:
- provide calorie targets
- recommend starvation
- recommend crash diets
- provide eating-disorder advice
- prescribe medication
- make medical diagnoses

Focus on balanced meals, hydration, sleep and recovery.
"""


def demo_tip(goal: str) -> str:

    return (
        f"For {goal}, focus on regular balanced meals containing "
        "protein foods, vegetables or fruit, whole grains or other "
        "starchy foods, and enough fluids. After activity, have a "
        "normal balanced meal or snack and prioritize good sleep "
        "and recovery."
    )


def generate_nutrition_tip_with_flash(
    goal: str
) -> str:

    settings = get_settings()

    if not settings.gemini_api_key:

        return demo_tip(goal)

    prompt = f"""
Give one concise nutrition or recovery tip.

Fitness goal:
{goal}

Requirements:
- Practical
- Balanced
- General wellness
- Maximum 100 words
- Mention hydration or recovery when appropriate
- No calorie prescriptions
- No restrictive diet instructions
"""

    try:

        return generate_text(
            prompt=prompt,
            model=settings.fast_model,
            system_instruction=SYSTEM_INSTRUCTION
        )

    except Exception:

        return demo_tip(goal)