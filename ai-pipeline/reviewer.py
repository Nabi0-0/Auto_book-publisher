from llm_client import (
    GROQ_MODEL,
    MAX_COMPLETION_TOKENS,
    REASONING_EFFORT,
    get_groq_client,
)

def check_source_fidelity(original_text: str, draft_text: str) -> str:
    if not isinstance(original_text, str) or not original_text.strip():
        raise ValueError("Original chapter cannot be empty.")

    if not isinstance(draft_text, str) or not draft_text.strip():
        raise ValueError("Draft chapter cannot be empty.")

    client = get_groq_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are a strict source-fidelity auditor.
Compare the draft against the original chapter.

Check for:
- Meaningful source events, facts, descriptions, relationships, or dialogue omitted
  from the draft.
- Events, facts, descriptions, relationships, or dialogue added without support
  from the source.
- Changes that alter the source's meaning or sequence.

Do not flag harmless wording changes or stylistic paraphrasing.

Return exactly one of:
PASS
FLAG: followed by a concise list of the most important omissions or unsupported additions.

Be conservative: flag only clear, meaningful fidelity problems.""",
            },
            {
                "role": "user",
                "content": (
                    f"ORIGINAL CHAPTER:\n{original_text}\n\n"
                    f"DRAFT CHAPTER:\n{draft_text}"
                ),
            },
        ],
        max_completion_tokens=MAX_COMPLETION_TOKENS,
        reasoning_effort=REASONING_EFFORT,
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise RuntimeError("The fidelity checker returned an empty response.")

    return result.strip()

def review_text_with_llama(
    original_text: str,
    draft_text: str,
    tone: str = "natural and polished",
) -> str:
    if not isinstance(original_text, str) or not original_text.strip():
        raise ValueError("Original chapter cannot be empty.")

    if not isinstance(draft_text, str) or not draft_text.strip():
        raise ValueError("Text to review cannot be empty.")

    client = get_groq_client()

    system_prompt = f"""You are an experienced book editor.
Revise the draft using the original chapter as the source of truth.

Requirements:
- Preserve the original story structure, events, characters, and relationships.
- Do not add events, details, dialogue, character traits, or descriptions that are
  not supported by the original chapter.
- If the draft contains unsupported details, remove them or correct them using
  only information from the original.
- Do not remove meaningful source information.
- Fix awkward phrasing and grammatical errors.
- Improve transitions, clarity, and readability.
- Maintain a {tone} tone without over-editing.
- Return only the revised chapter."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "ORIGINAL CHAPTER:\n"
                    f"{original_text}\n\n"
                    "DRAFT TO REVIEW:\n"
                    f"{draft_text}"
                ),
            },
        ],
        max_completion_tokens=MAX_COMPLETION_TOKENS,
        reasoning_effort=REASONING_EFFORT,
    )

    reviewed_text = response.choices[0].message.content

    if not reviewed_text or not reviewed_text.strip():
        raise RuntimeError("The reviewer returned an empty response.")

    return reviewed_text.strip()