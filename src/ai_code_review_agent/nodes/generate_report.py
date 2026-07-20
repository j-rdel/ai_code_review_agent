"""Node: render the Markdown report and write it to disk."""

from __future__ import annotations

from ai_code_review_agent.config import settings
from ai_code_review_agent.state import GraphState
from ai_code_review_agent.tools.report_writer import render_markdown, write_report


def generate_report(state: GraphState) -> dict:
    markdown = render_markdown(
        repo_name=state["repo_name"],
        base_ref=state["base_ref"],
        head_ref=state["head_ref"],
        file_reviews=state["file_reviews"],
        repo_summary=state["repo_summary"],
    )
    out_dir = state.get("output_dir") or settings.default_output_dir
    path = write_report(markdown, state["repo_name"], out_dir)
    return {
        "report_path": str(path),
        "report_markdown": markdown,
    }
