from pathlib import Path

from ai_code_review_agent.models import (
    FileReview,
    Issue,
    RepoSummary,
    SeverityCounts,
)
from ai_code_review_agent.tools.report_writer import render_markdown, write_report


def _sample_kwargs() -> dict:
    return dict(
        repo_name="myrepo",
        base_ref="main",
        head_ref="HEAD",
        file_reviews=[
            FileReview(
                file_path="src/foo.py",
                overall_score=7.5,
                summary="Solid module with a few nits.",
                issues=[
                    Issue(
                        category="bug",
                        severity="high",
                        line=12,
                        description="Off-by-one in loop bound.",
                        suggestion="Use `<=` instead of `<`.",
                    )
                ],
                strengths=["Clear naming.", "Good docstrings."],
            )
        ],
        repo_summary=RepoSummary(
            overall_assessment="Ship-ready with minor fixes.",
            total_issues_by_severity=SeverityCounts(high=1, low=2),
            top_priorities=["Fix off-by-one in foo.py."],
            recommendations=["Add unit tests for edge cases."],
        ),
    )


class TestRenderMarkdown:
    def test_contains_top_level_sections(self):
        md = render_markdown(**_sample_kwargs())
        assert "# AI Code Review — myrepo" in md
        assert "## Overall Assessment" in md
        assert "## Per-file reviews" in md

    def test_renders_ref_range(self):
        md = render_markdown(**_sample_kwargs())
        assert "`main`" in md
        assert "`HEAD`" in md

    def test_includes_file_review_details(self):
        md = render_markdown(**_sample_kwargs())
        assert "`src/foo.py`" in md
        assert "7.5/10" in md
        assert "Off-by-one in loop bound." in md
        assert "Use `<=` instead of `<`." in md
        assert "Clear naming." in md

    def test_renders_severity_totals(self):
        md = render_markdown(**_sample_kwargs())
        assert "| Critical | High | Medium | Low |" in md
        assert "| 0 | 1 | 0 | 2 |" in md

    def test_lists_priorities_and_recommendations(self):
        md = render_markdown(**_sample_kwargs())
        assert "- Fix off-by-one in foo.py." in md
        assert "- Add unit tests for edge cases." in md

    def test_omits_empty_sections(self):
        kwargs = _sample_kwargs()
        kwargs["repo_summary"] = RepoSummary(overall_assessment="All good.")
        md = render_markdown(**kwargs)
        assert "### Top priorities" not in md
        assert "### Recommendations" not in md


class TestWriteReport:
    def test_writes_file_with_expected_name(self, tmp_path: Path):
        path = write_report(
            markdown="# hello\n", repo_name="myrepo", out_dir=tmp_path
        )
        assert path.exists()
        assert path.parent == tmp_path.resolve()
        assert path.name.startswith("myrepo_")
        assert path.suffix == ".md"
        assert path.read_text(encoding="utf-8") == "# hello\n"

    def test_creates_missing_out_dir(self, tmp_path: Path):
        target = tmp_path / "nested" / "reports"
        path = write_report(markdown="x", repo_name="r", out_dir=target)
        assert path.parent == target.resolve()
