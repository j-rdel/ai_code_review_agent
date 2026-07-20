import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from ai_code_review_agent.cli import app
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


def _stub_llms(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_review_llm(*args, **kwargs):
        structured = MagicMock()

        def _invoke(messages):
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

    def fake_summary_llm(*args, **kwargs):
        structured = MagicMock()
        structured.invoke.return_value = RepoSummary(
            overall_assessment="CLI smoke ok.",
            total_issues_by_severity=SeverityCounts(),
        )
        llm = MagicMock()
        llm.with_structured_output.return_value = structured
        return llm

    monkeypatch.setattr(review_module, "get_llm", fake_review_llm)
    monkeypatch.setattr(agg_module, "get_llm", fake_summary_llm)


class TestCli:
    def test_help_lists_all_options(self):
        result = CliRunner().invoke(app, ["--help"])
        assert result.exit_code == 0
        for opt in ("--repo", "--base", "--head", "--out"):
            assert opt in result.stdout

    def test_end_to_end_writes_report(
        self,
        repo: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        base = _git(repo, "rev-parse", "HEAD").strip()
        (repo / "a.py").write_text("print('a2')\n")
        _commit(repo, "second")

        _stub_llms(monkeypatch)

        out_dir = tmp_path / "reports"
        result = CliRunner().invoke(
            app,
            [
                "--repo",
                str(repo),
                "--base",
                base,
                "--head",
                "HEAD",
                "--out",
                str(out_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Report written:" in result.output
        assert "Reviewed 1 file(s)." in result.output

        reports = list(out_dir.glob("myrepo_*.md"))
        assert len(reports) == 1
        assert "CLI smoke ok." in reports[0].read_text()
