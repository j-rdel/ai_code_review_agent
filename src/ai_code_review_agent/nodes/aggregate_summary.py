"""Node: synthesize per-file reviews into a repository-level summary."""

from __future__ import annotations

import json

from ai_code_review_agent.llm import get_llm
from ai_code_review_agent.models import RepoSummary
from ai_code_review_agent.prompts import AGGREGATE_PROMPT
from ai_code_review_agent.state import GraphState


def aggregate_summary(state: GraphState) -> dict:
    reviews = state.get("file_reviews") or []
    reviews_json = json.dumps(
        [r.model_dump() for r in reviews], indent=2, ensure_ascii=False
    )

    structured = get_llm().with_structured_output(RepoSummary)
    messages = AGGREGATE_PROMPT.format_messages(reviews_json=reviews_json)
    summary = structured.invoke(messages)

    return {"repo_summary": summary}
