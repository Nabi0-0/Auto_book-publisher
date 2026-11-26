
from llm_client import (
    GROQ_MODEL,
    MAX_COMPLETION_TOKENS,
    REASONING_EFFORT,
    get_groq_client,
)


def spin_text_with_llama(
    chapter_text: str,
    tone: str = "modern and engaging",
) -> str:
    if not isinstance(chapter_text, str) or not chapter_text.strip():
        raise ValueError("Chapter text cannot be empty.")

    client = get_groq_client()

    system_prompt = (
        f"You are an AI writer. Rewrite the following story in a {tone} tone. "
        "Preserve all events, characters, and their relationships. "
        "Improve clarity, pacing, and readability without inventing events."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chapter_text},
        ],
        max_completion_tokens=MAX_COMPLETION_TOKENS,
        reasoning_effort=REASONING_EFFORT,
    )

    generated_text = response.choices[0].message.content

    if not generated_text or not generated_text.strip():
        raise RuntimeError("The writer returned an empty response.")

    return generated_text.strip()
