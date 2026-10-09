from functools import lru_cache

from google import genai

from .config import get_settings


@lru_cache
def get_gemini_client():

    settings = get_settings()

    if not settings.gemini_api_key:
        return None

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(
    prompt: str,
    model: str,
    system_instruction: str | None = None
) -> str:

    client = get_gemini_client()

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured."
        )

    config = None

    if system_instruction:
        config = {
            "system_instruction": system_instruction
        }

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    text = getattr(
        response,
        "text",
        None
    )

    if not text:
        raise RuntimeError(
            "Gemini returned no text."
        )

    return text.strip()