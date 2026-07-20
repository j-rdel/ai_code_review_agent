"""Node: read full content of every changed file at the head ref."""

from __future__ import annotations

from ai_code_review_agent.state import GraphState
from ai_code_review_agent.tools.git_tools import read_file_at_ref


def load_files(state: GraphState) -> dict:
    """Populate `file_contents` with each changed file's full content."""
    repo_path = state["repo_path"]
    head_ref = state["head_ref"]
    contents = {
        path: read_file_at_ref(repo_path, path, head_ref)
        for path in state["changed_files"]
    }
    return {"file_contents": contents}
