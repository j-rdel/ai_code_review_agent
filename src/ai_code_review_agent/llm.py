"""ChatOllama factory used by review and aggregation nodes."""

from __future__ import annotations

from langchain_ollama import ChatOllama

from ai_code_review_agent.config import settings


def get_llm(temperature: float | None = None) -> ChatOllama:
    """Return a configured `ChatOllama` instance.

    `temperature` overrides the configured default when provided.
    """
    return ChatOllama(
        model=settings.model,
        base_url=settings.ollama_host,
        temperature=settings.temperature if temperature is None else temperature,
    )
