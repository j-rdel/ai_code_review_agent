from ai_code_review_agent.prompts import AGGREGATE_PROMPT, FILE_REVIEW_PROMPT


def _rendered_text(prompt, **kwargs) -> str:
    messages = prompt.format_messages(**kwargs)
    return "\n".join(m.content for m in messages)


class TestFileReviewPrompt:
    def test_disables_qwen3_thinking(self):
        text = _rendered_text(
            FILE_REVIEW_PROMPT, file_path="x.py", content="print('hi')"
        )
        assert "/no_think" in text

    def test_includes_file_path_and_content(self):
        text = _rendered_text(
            FILE_REVIEW_PROMPT,
            file_path="src/foo.py",
            content="def bar():\n    pass\n",
        )
        assert "`src/foo.py`" in text
        assert "def bar():" in text

    def test_produces_two_messages(self):
        msgs = FILE_REVIEW_PROMPT.format_messages(
            file_path="x.py", content="x"
        )
        assert [m.type for m in msgs] == ["system", "human"]


class TestAggregatePrompt:
    def test_disables_qwen3_thinking(self):
        text = _rendered_text(AGGREGATE_PROMPT, reviews_json="[]")
        assert "/no_think" in text

    def test_includes_reviews_json_payload(self):
        payload = '[{"file_path": "x.py"}]'
        text = _rendered_text(AGGREGATE_PROMPT, reviews_json=payload)
        assert payload in text

    def test_produces_two_messages(self):
        msgs = AGGREGATE_PROMPT.format_messages(reviews_json="[]")
        assert [m.type for m in msgs] == ["system", "human"]
