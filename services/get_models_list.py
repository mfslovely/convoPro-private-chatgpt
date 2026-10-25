"""Retrieve the models installed on the configured Ollama server."""

from ollama import Client

from config.settings import Settings


settings = Settings()


def get_models_list() -> list[str]:
    """Return installed Ollama model names in alphabetical order."""

    client = Client(host=settings.OLLAMA_URL)
    response = client.list()

    return sorted(
        model.model
        for model in response.models
        if model.model
    )


# Descriptive alias for callers that prefer this name.
get_available_models = get_models_list
