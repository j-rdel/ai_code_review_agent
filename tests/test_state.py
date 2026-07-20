from typing import get_type_hints

from langgraph.graph import StateGraph

from ai_code_review_agent.models import FileReview
from ai_code_review_agent.state import GraphState


class TestGraphState:
    def test_typeddict_is_total_false(self):
        # Partial state must be permitted (nodes fill state progressively).
        assert GraphState.__total__ is False

    def test_declares_expected_keys(self):
        hints = get_type_hints(GraphState, include_extras=True)
        expected = {
            "repo_path",
            "base_ref",
            "head_ref",
            "repo_name",
            "changed_files",
            "file_contents",
            "file_reviews",
            "repo_summary",
            "report_path",
            "report_markdown",
        }
        assert expected.issubset(hints.keys())

    def test_file_reviews_reducer_concatenates_via_langgraph(self):
        """Compile a tiny graph that fans in two review lists.

        LangGraph applies the `operator.add` reducer on `file_reviews` when
        multiple nodes return partial state — this is the mechanism that lets
        parallel `Send`s accumulate reviews.
        """
        r1 = FileReview(file_path="a.py", overall_score=8.0, summary="ok")
        r2 = FileReview(file_path="b.py", overall_score=6.0, summary="meh")

        builder = StateGraph(GraphState)
        builder.add_node("emit_a", lambda s: {"file_reviews": [r1]})
        builder.add_node("emit_b", lambda s: {"file_reviews": [r2]})
        builder.set_entry_point("emit_a")
        builder.add_edge("emit_a", "emit_b")
        builder.set_finish_point("emit_b")
        graph = builder.compile()

        final = graph.invoke({"file_reviews": []})
        assert [fr.file_path for fr in final["file_reviews"]] == ["a.py", "b.py"]
