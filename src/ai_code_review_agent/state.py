"""Shared state that flows through every node of the LangGraph."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from ai_code_review_agent.models import FileReview, RepoSummary


class GraphState(TypedDict, total=False):
    """State shared across all nodes.

    `total=False` because the state is populated progressively — the initial
    invocation only sets input fields; downstream nodes fill in the rest.

    `file_reviews` uses `operator.add` as reducer so parallel `review_file`
    executions (fan-out via `Send`) can append safely; LangGraph merges them
    with list concatenation on fan-in.
    """

    # inputs
    repo_path: str
    base_ref: str
    head_ref: str

    # discovery
    repo_name: str
    changed_files: list[str]

    # loaded content (path -> full file content)
    file_contents: dict[str, str]

    # accumulated across parallel review nodes
    file_reviews: Annotated[list[FileReview], operator.add]

    # synthesis
    repo_summary: RepoSummary | None

    # output
    report_path: str | None
    report_markdown: str | None
