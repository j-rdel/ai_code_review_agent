import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_code_review_agent.graph import build_graph, route_files
from ai_code_review_agent.models import FileReview, RepoSummary, SeverityCounts
from ai_code_review_agent.nodes import aggregate_summary as agg_module
from ai_code_review_agent.nodes import review_file as review_module


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
    (r / "seed.py").write_text("print('seed')\n")
    _commit(r, "initial")
    return r


def _stub_review_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every `review_file` LLM call return a FileReview with the sent path."""

    def fake_get_llm(*args, **kwargs):
        structured = MagicMock()

        def _invoke(messages):
            # extract file path from human message so each review is distinct
            human = messages[-1].content
            marker = "File: `"
            start = human.index(marker) + len(marker)
            end = human.index("`", start)
            path = human[start:end]
            return FileReview(
                file_path=path, overall_score=8.0, summary=f"review of {path}"
            )

        structured.invoke.side_effect = _invoke
        llm = MagicMock()
        llm.with_structured_output.return_value = structured
        return llm

    monkeypatch.setattr(review_module, "get_llm", fake_get_llm)


def _stub_summary_llm(
    monkeypatch: pytest.MonkeyPatch, summary: RepoSummary
) -> None:
    structured = MagicMock()
    structured.invoke.return_value = summary
    llm = MagicMock()
    llm.with_structured_output.return_value = structured
    monkeypatch.setattr(agg_module, "get_llm", lambda: llm)


class TestRouteFiles:
    def test_fans_out_one_send_per_file(self):
        state = {
            "file_contents": {"a.py": "print('a')", "b.py": "print('b')"}
        }
        result = route_files(state)
        assert isinstance(result, list)
        assert {s.node for s in result} == {"review_file"}
        payloads = {s.arg["file_path"] for s in result}
        assert payloads == {"a.py", "b.py"}

    def test_short_circuits_when_no_files(self):
        assert route_files({"file_contents": {}}) == "aggregate_summary"
        assert route_files({}) == "aggregate_summary"


class TestBuildGraph:
    def test_end_to_end_happy_path(
        self,
        repo: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        base = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "a.py").write_text("print('a2')\n")
        (repo / "b.py").write_text("print('b')\n")
        (repo / "docs.md").write_text("nope")
        _commit(repo, "second")

        _stub_review_llm(monkeypatch)
        _stub_summary_llm(
            monkeypatch,
            RepoSummary(
                overall_assessment="Fan-out fan-in worked.",
                total_issues_by_severity=SeverityCounts(),
            ),
        )

        out_dir = tmp_path / "reports"
        graph = build_graph()
        final = graph.invoke(
            {
                "repo_path": str(repo),
                "base_ref": base,
                "head_ref": "HEAD",
                "output_dir": str(out_dir),
                "file_reviews": [],
            }
        )

        # Both changed .py files were reviewed (fan-in via reducer).
        reviewed_paths = {fr.file_path for fr in final["file_reviews"]}
        assert reviewed_paths == {"a.py", "b.py"}

        # Aggregation ran.
        assert final["repo_summary"].overall_assessment == "Fan-out fan-in worked."

        # Report file was written.
        report_path = Path(final["report_path"])
        assert report_path.exists()
        assert report_path.parent == out_dir.resolve()
        assert "Fan-out fan-in worked." in report_path.read_text()

    def test_end_to_end_no_python_changes(
        self,
        repo: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        base = _git(repo, "rev-parse", "HEAD").strip()
        (repo / "docs.md").write_text("only docs")
        _commit(repo, "docs only")

        # review LLM should NOT be called; still stub it to catch accidental use.
        _stub_review_llm(monkeypatch)
        _stub_summary_llm(
            monkeypatch,
            RepoSummary(overall_assessment="No Python changes."),
        )

        out_dir = tmp_path / "reports"
        graph = build_graph()
        final = graph.invoke(
            {
                "repo_path": str(repo),
                "base_ref": base,
                "head_ref": "HEAD",
                "output_dir": str(out_dir),
                "file_reviews": [],
            }
        )

        assert final["file_reviews"] == []
        assert Path(final["report_path"]).exists()
