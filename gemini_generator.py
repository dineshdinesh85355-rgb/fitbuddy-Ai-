from .config import get_settings
from .gemini_client import generate_text


SYSTEM_INSTRUCTION = """
You are FitBuddy, a general wellness and fitness planning assistant.

Create safe, practical and age-appropriate general wellness guidance.

Do not:
- diagnose medical conditions
- prescribe medication
- provide extreme exercise challenges
- provide dangerous exercise instructions
- provide starvation or crash-diet instructions
- provide calorie restriction targets
- judge someone's appearance

For younger users, keep recommendations age-appropriate and encourage
support from a parent, guardian, qualified coach, or healthcare professional
when appropriate.

Focus on:
- gradual progress
- recovery
- hydration
- balanced eating
- sleep
- safe movement
"""


def demo_plan(
    goal: str,
    intensity: str
) -> str:

    return f"""
FITBUDDY – 7 DAY DEMO WORKOUT PLAN

Goal:
{goal}

Intensity:
{intensity.title()}


DAY 1 – FULL BODY

Warm-up:
5–8 minutes of comfortable movement.

Main workout:
• Bodyweight squats – 2–3 sets × 8–12 reps
• Wall/incline push-ups – 2–3 sets × 8–12 reps
• Glute bridges – 2–3 sets × 10–15 reps

Cooldown:
Easy walking and gentle stretching.


DAY 2 – CARDIO + MOBILITY

Warm-up:
5 minutes easy movement.

Main workout:
20–30 minutes comfortable walking or cycling.

Mobility:
8–10 minutes of gentle mobility exercises.

Cooldown:
Slow walking and relaxed breathing.


DAY 3 – UPPER BODY + CORE

Warm-up:
5–8 minutes.

Main workout:
• Incline push-ups – 2–3 × 8–12
• Resistance-band rows – 2–3 × 8–12
• Dead bugs – 2–3 × 6–10 per side

Cooldown:
Gentle stretching.


DAY 4 – RECOVERY

Take a recovery day.

Optional:
Easy walking and light mobility.


DAY 5 – LOWER BODY

Warm-up:
5–8 minutes.

Main workout:
• Squat to chair – 2–3 × 8–12
• Step-ups – 2–3 × 6–10 each side
• Calf raises – 2–3 × 10–15

Cooldown:
Gentle stretching.


DAY 6 – ENJOYABLE MOVEMENT

Choose a safe activity you enjoy:

• Walking
• Cycling
• Dancing
• Recreational sport

20–40 minutes at a comfortable level.


DAY 7 – REST + REFLECTION

Rest or take an easy walk.

Think about:
• What felt comfortable?
• What was difficult?
• What would you like to change?


SAFETY

Progress gradually.

Stop activity if you experience pain, dizziness,
faintness or unusual shortness of breath.
"""


def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:

    settings = get_settings()

    # Demo mode if no API key
    if not settings.gemini_api_key:

        return demo_plan(
            goal,
            intensity
        )

    prompt = f"""
Create a personalized 7-day general wellness workout plan.

User information:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Preferred Intensity: {intensity}

Requirements:

1. Create Day 1 through Day 7.
2. Include at least one recovery/rest day.
3. Include warm-up for active days.
4. Include main exercises or activities.
5. Give reasonable sets/repetitions or durations.
6. Include cooldown or recovery guidance.
7. Make the plan practical and easy to understand.
8. Progress gradually.
9. Avoid extreme exercise.
10. Do not provide calorie restriction instructions.
11. Do not provide medical diagnosis or treatment.
12. End with a short safety note.

Return the complete plan as readable text.
"""

    try:

        return generate_text(
            prompt=prompt,
            model=settings.workout_model,
            system_instruction=SYSTEM_INSTRUCTION
        )

    except Exception:

        return demo_plan(
            goal,
            intensity
        )