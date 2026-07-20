import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_code_review_agent.models import (
    FileReview,
    Issue,
    RepoSummary,
    SeverityCounts,
)
from ai_code_review_agent.nodes import aggregate_summary as agg_module
from ai_code_review_agent.nodes import generate_report as gr_module
from ai_code_review_agent.nodes import review_file as review_module
from ai_code_review_agent.nodes.aggregate_summary import aggregate_summary
from ai_code_review_agent.nodes.detect_changes import detect_changes
from ai_code_review_agent.nodes.generate_report import generate_report
from ai_code_review_agent.nodes.load_files import load_files
from ai_code_review_agent.nodes.review_file import review_file


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "myrepo"
    r.mkdir()
    _git(r, "init", "-b", "main")
    _git(r, "config", "user.email", "test@example.com")
    _git(r, "config", "user.name", "Test")
    _git(r, "config", "commit.gpgsign", "false")
    return r


class TestDetectChanges:
    def test_returns_changed_py_and_repo_name(self, repo: Path):
        (repo / "a.py").write_text("print('a')\n")
        _commit(repo, "initial")
        base = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "a.py").write_text("print('a2')\n")
        (repo / "b.py").write_text("print('b')\n")
        (repo / "notes.md").write_text("nope")
        _commit(repo, "second")

        result = detect_changes(
            {"repo_path": str(repo), "base_ref": base, "head_ref": "HEAD"}
        )
        assert set(result["changed_files"]) == {"a.py", "b.py"}
        assert result["repo_name"] == "myrepo"

    def test_empty_when_no_py_changes(self, repo: Path):
        (repo / "a.py").write_text("x\n")
        _commit(repo, "initial")
        base = _git(repo, "rev-parse", "HEAD").strip()
        (repo / "readme.md").write_text("hi\n")
        _commit(repo, "docs only")

        result = detect_changes(
            {"repo_path": str(repo), "base_ref": base, "head_ref": "HEAD"}
        )
        assert result["changed_files"] == []


class TestLoadFiles:
    def test_reads_content_at_head(self, repo: Path):
        (repo / "a.py").write_text("print('a')\n")
        (repo / "b.py").write_text("def foo():\n    pass\n")
        _commit(repo, "initial")

        result = load_files(
            {
                "repo_path": str(repo),
                "head_ref": "HEAD",
                "changed_files": ["a.py", "b.py"],
            }
        )
        assert result["file_contents"] == {
            "a.py": "print('a')\n",
            "b.py": "def foo():\n    pass\n",
        }

    def test_no_changed_files_returns_empty_dict(self, repo: Path):
        (repo / "a.py").write_text("x\n")
        _commit(repo, "initial")
        result = load_files(
            {"repo_path": str(repo), "head_ref": "HEAD", "changed_files": []}
        )
        assert result["file_contents"] == {}


class TestReviewFile:
    def test_invokes_llm_with_structured_output_and_wraps_result(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        # LLM would return a review with the wrong file_path (hallucination).
        llm_review = FileReview(
            file_path="wrong_name.py",
            overall_score=7.0,
            summary="Looks fine.",
        )
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = llm_review
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        monkeypatch.setattr(review_module, "get_llm", lambda: mock_llm)

        result = review_file(
            {"file_path": "src/actual.py", "content": "print('x')"}
        )

        # Structured output was requested with the FileReview schema.
        mock_llm.with_structured_output.assert_called_once_with(FileReview)
        # Result is wrapped as a single-element list (fan-in via reducer).
        assert list(result.keys()) == ["file_reviews"]
        assert len(result["file_reviews"]) == 1
        # file_path is overwritten by the node — never trust the LLM's echo.
        assert result["file_reviews"][0].file_path == "src/actual.py"

    def test_messages_include_file_path_and_content(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = FileReview(
            file_path="x.py", overall_score=9.0, summary="ok"
        )
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        monkeypatch.setattr(review_module, "get_llm", lambda: mock_llm)

        review_file(
            {"file_path": "src/foo.py", "content": "def bar():\n    pass\n"}
        )

        messages = mock_structured.invoke.call_args.args[0]
        rendered = "\n".join(m.content for m in messages)
        assert "src/foo.py" in rendered
        assert "def bar():" in rendered


class TestAggregateSummary:
    def test_serializes_reviews_and_returns_summary(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        expected = RepoSummary(
            overall_assessment="Solid change.",
            total_issues_by_severity=SeverityCounts(medium=1),
        )
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = expected
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        monkeypatch.setattr(agg_module, "get_llm", lambda: mock_llm)

        reviews = [
            FileReview(
                file_path="a.py",
                overall_score=8.0,
                summary="fine",
                issues=[
                    Issue(
                        category="style",
                        severity="medium",
                        description="d",
                        suggestion="s",
                    )
                ],
            )
        ]
        result = aggregate_summary({"file_reviews": reviews})

        mock_llm.with_structured_output.assert_called_once_with(RepoSummary)
        # The human message must carry a JSON serialization of the reviews.
        messages = mock_structured.invoke.call_args.args[0]
        human_text = messages[-1].content
        # find the JSON block and parse it — validates it's real JSON.
        payload_start = human_text.index("[")
        parsed = json.loads(human_text[payload_start:])
        assert parsed[0]["file_path"] == "a.py"
        assert parsed[0]["issues"][0]["category"] == "style"

        assert result == {"repo_summary": expected}


class TestGenerateReport:
    def test_writes_markdown_file_and_returns_paths(self, tmp_path: Path):
        review = FileReview(
            file_path="foo.py", overall_score=8.0, summary="ok"
        )
        summary = RepoSummary(overall_assessment="All good.")
        state = {
            "repo_name": "myrepo",
            "base_ref": "main",
            "head_ref": "HEAD",
            "file_reviews": [review],
            "repo_summary": summary,
            "output_dir": str(tmp_path),
        }
        result = generate_report(state)

        report_path = Path(result["report_path"])
        assert report_path.exists()
        assert report_path.parent == tmp_path.resolve()
        assert report_path.name.startswith("myrepo_")
        assert "# AI Code Review — myrepo" in result["report_markdown"]
        assert report_path.read_text() == result["report_markdown"]

    def test_falls_back_to_settings_output_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        from ai_code_review_agent.config import Settings

        monkeypatch.setattr(
            gr_module,
            "settings",
            Settings(default_output_dir=str(tmp_path / "fallback")),
        )
        state = {
            "repo_name": "r",
            "base_ref": "main",
            "head_ref": "HEAD",
            "file_reviews": [
                FileReview(file_path="x.py", overall_score=5.0, summary="x")
            ],
            "repo_summary": RepoSummary(overall_assessment="x"),
        }
        result = generate_report(state)
        assert Path(result["report_path"]).parent == (
            tmp_path / "fallback"
        ).resolve()
