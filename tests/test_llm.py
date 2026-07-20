import pytest
from langchain_ollama import ChatOllama

from ai_code_review_agent import llm as llm_module
from ai_code_review_agent.config import Settings
from ai_code_review_agent.llm import get_llm


@pytest.fixture
def fake_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Swap module-level `settings` for a controlled Settings instance."""
    s = Settings(
        model="qwen3:test",
        ollama_host="http://ollama.test:1234",
        temperature=0.3,
    )
    monkeypatch.setattr(llm_module, "settings", s)
    return s


class TestGetLlm:
    def test_returns_chat_ollama_instance(self, fake_settings: Settings):
        assert isinstance(get_llm(), ChatOllama)

    def test_uses_configured_model_and_host(self, fake_settings: Settings):
        client = get_llm()
        assert client.model == "qwen3:test"
        assert client.base_url == "http://ollama.test:1234"

    def test_uses_configured_temperature_by_default(
        self, fake_settings: Settings
    ):
        assert get_llm().temperature == 0.3

    def test_temperature_override(self, fake_settings: Settings):
        assert get_llm(temperature=0.0).temperature == 0.0
