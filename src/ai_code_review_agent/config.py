"""Runtime settings, loaded from environment with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Immutable configuration for the agent."""

    model: str = "qwen3:8b"
    ollama_host: str = "http://localhost:11434"
    temperature: float = 0.2
    default_base_ref: str = "main"
    default_head_ref: str = "HEAD"
    default_output_dir: str = "reports"


def load_settings() -> Settings:
    """Build a Settings instance from environment variables."""
    return Settings(
        model=os.environ.get("OLLAMA_MODEL", "qwen3:8b"),
        ollama_host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        temperature=float(os.environ.get("OLLAMA_TEMPERATURE", "0.2")),
    )


settings = load_settings()
