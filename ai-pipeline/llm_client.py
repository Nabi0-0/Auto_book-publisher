
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env.local"


load_dotenv(dotenv_path=ENV_FILE)


def get_required_setting(name: str) -> str:
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value.strip()


def get_max_completion_tokens() -> int:
    raw_value = get_required_setting("GROQ_MAX_COMPLETION_TOKENS")

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            "GROQ_MAX_COMPLETION_TOKENS must be an integer"
        ) from exc

    if value < 1:
        raise RuntimeError(
            "GROQ_MAX_COMPLETION_TOKENS must be greater than zero"
        )

    return value


GROQ_MODEL = get_required_setting("GROQ_MODEL")
MAX_COMPLETION_TOKENS = get_max_completion_tokens()
REASONING_EFFORT = get_required_setting("GROQ_REASONING_EFFORT")


@lru_cache(maxsize=1)
def get_groq_client() -> OpenAI:
    api_key = get_required_setting("GROQ_API_KEY")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=60.0,
        max_retries=2,
    )
