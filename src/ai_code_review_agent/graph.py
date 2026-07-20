"""LangGraph flow assembly.

Wires the five nodes into a directed graph:

    START → detect_changes → load_files
                                │
                                ▼  (Send fan-out, one per file)
                          review_file  ── reducer ──┐
                                                    ▼
                                          aggregate_summary
                                                    │
                                                    ▼
                                          generate_report → END

`review_file` receives a minimal `{file_path, content}` dict per invocation
via `Send`; results are merged back into `file_reviews` through the
`operator.add` reducer declared on `GraphState`. When no Python files
changed, `route_files` short-circuits directly to `aggregate_summary`.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from ai_code_review_agent.nodes.aggregate_summary import aggregate_summary
from ai_code_review_agent.nodes.detect_changes import detect_changes
from ai_code_review_agent.nodes.generate_report import generate_report
from ai_code_review_agent.nodes.load_files import load_files
from ai_code_review_agent.nodes.review_file import review_file
from ai_code_review_agent.state import GraphState


def route_files(state: GraphState) -> list[Send] | str:
    """Fan out one `review_file` per changed file; skip to aggregation if none."""
    files = state.get("file_contents") or {}
    if not files:
        return "aggregate_summary"
    return [
        Send("review_file", {"file_path": path, "content": content})
        for path, content in files.items()
    ]


def build_graph():
    """Compile the LangGraph agent."""
    builder = StateGraph(GraphState)
    builder.add_node("detect_changes", detect_changes)
    builder.add_node("load_files", load_files)
    builder.add_node("review_file", review_file)
    builder.add_node("aggregate_summary", aggregate_summary)
    builder.add_node("generate_report", generate_report)

    builder.add_edge(START, "detect_changes")
    builder.add_edge("detect_changes", "load_files")
    builder.add_conditional_edges(
        "load_files", route_files, ["review_file", "aggregate_summary"]
    )
    builder.add_edge("review_file", "aggregate_summary")
    builder.add_edge("aggregate_summary", "generate_report")
    builder.add_edge("generate_report", END)

    return builder.compile()
