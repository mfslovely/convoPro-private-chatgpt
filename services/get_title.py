"""Generate concise conversation titles with Ollama."""

import re

from llm_factory.get_llm import get_ollama_llm


DEFAULT_TITLE = "Untitled Conversation"
MAX_TITLE_LENGTH = 60


def _fallback_title(message: str) -> str:
    """Build a deterministic title when model generation is unavailable."""

    compact_message = " ".join(message.split()).strip()
    if not compact_message:
        return DEFAULT_TITLE

    return compact_message[:MAX_TITLE_LENGTH].rstrip(" ,.;:-")


def get_title(message: str, model_name: str) -> str:
    """Generate a short title for the first user message."""

    fallback = _fallback_title(message)
    if fallback == DEFAULT_TITLE:
        return fallback

    prompt = (
        "Create a concise title for the following chat message. "
        "Use at most six words. Return only the title, without quotation "
        "marks, markdown, or punctuation at the end.\n\n"
        f"Message: {message.strip()}\n\nTitle:"
    )

    try:
        generated = get_ollama_llm(model_name).invoke(prompt)
    except Exception:
        return fallback

    title = " ".join(str(generated).splitlines()[0].split())
    title = re.sub(r"^[\"'`]+|[\"'`]+$", "", title)
    title = title.rstrip(" .,:;!?-")

    return title[:MAX_TITLE_LENGTH].strip() or fallback


generate_title = get_title
