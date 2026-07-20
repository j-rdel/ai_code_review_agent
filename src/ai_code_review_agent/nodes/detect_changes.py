"""Node: discover changed Python files between two git refs."""

from __future__ import annotations

from ai_code_review_agent.state import GraphState
from ai_code_review_agent.tools.git_tools import (
    get_repo_name,
    list_changed_python_files,
)


def detect_changes(state: GraphState) -> dict:
    """Populate `changed_files` and `repo_name` from the input refs."""
    repo_path = state["repo_path"]
    base_ref = state["base_ref"]
    head_ref = state["head_ref"]
    return {
        "changed_files": list_changed_python_files(
            repo_path, base_ref, head_ref
        ),
        "repo_name": get_repo_name(repo_path),
    }
