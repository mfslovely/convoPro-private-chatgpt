"""Create and cache LangChain clients for the local Ollama server."""

from langchain_ollama import OllamaLLM

from config.settings import Settings


settings = Settings()
OLLAMA_URL = settings.OLLAMA_URL.rstrip("/")

# Module-level cache for the most recently selected model and its instance.
_current_model_name: str | None = None
_current_llm_instance: OllamaLLM | None = None


def get_ollama_llm(model_name: str) -> OllamaLLM:
    """Return a cached LangChain Ollama client for ``model_name``."""

    global _current_model_name, _current_llm_instance

    model_name = model_name.strip()
    if not model_name:
        raise ValueError("Model name must not be empty.")

    if (
        _current_model_name == model_name
        and _current_llm_instance is not None
    ):
        return _current_llm_instance

    llm = OllamaLLM(
        base_url=OLLAMA_URL,
        model=model_name,
        validate_model_on_init=True,
    )

    _current_model_name = model_name
    _current_llm_instance = llm

    return llm


# Backward-compatible name for callers using the previous factory function.
get_llm = get_ollama_llm


# Example usage:
# check_llm = get_ollama_llm(model_name="gemma2:2b")
# print(check_llm)
# print(type(check_llm))
