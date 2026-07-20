"""Node: review one file with the LLM (fan-out worker).

Called via `Send` from `graph.py`, once per changed file, so the input state
here is a minimal `{"file_path": ..., "content": ...}` — not the full
`GraphState`. The return dict is merged back into `GraphState.file_reviews`
via the `operator.add` reducer.
"""

from __future__ import annotations

from ai_code_review_agent.llm import get_llm
from ai_code_review_agent.models import FileReview
from ai_code_review_agent.prompts import FILE_REVIEW_PROMPT


def review_file(state: dict) -> dict:
    file_path = state["file_path"]
    content = state["content"]

    structured = get_llm().with_structured_output(FileReview)
    messages = FILE_REVIEW_PROMPT.format_messages(
        file_path=file_path, content=content
    )
    review = structured.invoke(messages)

    # The LLM may hallucinate `file_path`; enforce the real one so the report
    # never displays a wrong filename.
    review.file_path = file_path

    return {"file_reviews": [review]}
