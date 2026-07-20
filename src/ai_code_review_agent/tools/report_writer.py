"""Render and persist the code-review Markdown report."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ai_code_review_agent.models import FileReview, RepoSummary


def render_markdown(
    *,
    repo_name: str,
    base_ref: str,
    head_ref: str,
    file_reviews: list[FileReview],
    repo_summary: RepoSummary,
) -> str:
    """Render the full review report as Markdown.

    Takes explicit fields rather than the whole graph state so the function
    stays testable in isolation. The `generate_report` node composes it from
    the state.
    """
    lines: list[str] = []
    lines.append(f"# AI Code Review — {repo_name}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"**Base:** `{base_ref}` → **Head:** `{head_ref}`")
    lines.append(f"**Files reviewed:** {len(file_reviews)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Overall Assessment")
    lines.append("")
    lines.append(repo_summary.overall_assessment)
    lines.append("")

    counts = repo_summary.total_issues_by_severity
    lines.append("### Issues by severity")
    lines.append("")
    lines.append("| Critical | High | Medium | Low |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(
        f"| {counts.critical} | {counts.high} | {counts.medium} | {counts.low} |"
    )
    lines.append("")

    if repo_summary.top_priorities:
        lines.append("### Top priorities")
        lines.append("")
        for priority in repo_summary.top_priorities:
            lines.append(f"- {priority}")
        lines.append("")

    if repo_summary.recommendations:
        lines.append("### Recommendations")
        lines.append("")
        for rec in repo_summary.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Per-file reviews")
    lines.append("")

    for review in file_reviews:
        lines.append(
            f"### `{review.file_path}` — score **{review.overall_score:.1f}/10**"
        )
        lines.append("")
        lines.append(review.summary)
        lines.append("")

        if review.issues:
            lines.append(f"**Issues ({len(review.issues)}):**")
            lines.append("")
            for issue in review.issues:
                loc = f", line {issue.line}" if issue.line is not None else ""
                lines.append(
                    f"- **[{issue.severity.upper()}]** _({issue.category}{loc})_ "
                    f"{issue.description}"
                )
                lines.append(f"  _Suggestion:_ {issue.suggestion}")
            lines.append("")

        if review.strengths:
            lines.append("**Strengths:**")
            lines.append("")
            for strength in review.strengths:
                lines.append(f"- {strength}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def write_report(markdown: str, repo_name: str, out_dir: str | Path) -> Path:
    """Write `markdown` to `<out_dir>/<repo_name>_<YYYYMMDD-HHMMSS>.md`.

    Creates `out_dir` if it does not exist. Returns the absolute path written.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out / f"{repo_name}_{timestamp}.md"
    path.write_text(markdown, encoding="utf-8")
    return path.resolve()
