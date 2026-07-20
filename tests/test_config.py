import pytest

from ai_code_review_agent.config import Settings, load_settings


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.model == "qwen3:8b"
        assert s.ollama_host == "http://localhost:11434"
        assert s.temperature == 0.2
        assert s.default_base_ref == "main"
        assert s.default_head_ref == "HEAD"
        assert s.default_output_dir == "reports"


class TestLoadSettings:
    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("OLLAMA_MODEL", "qwen3:32b")
        monkeypatch.setenv("OLLAMA_HOST", "http://ollama.internal:11434")
        monkeypatch.setenv("OLLAMA_TEMPERATURE", "0.7")
        s = load_settings()
        assert s.model == "qwen3:32b"
        assert s.ollama_host == "http://ollama.internal:11434"
        assert s.temperature == 0.7

    def test_uses_defaults_when_env_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        monkeypatch.delenv("OLLAMA_TEMPERATURE", raising=False)
        s = load_settings()
        assert s.model == "qwen3:8b"
        assert s.temperature == 0.2
