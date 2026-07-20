"""Prompt templates for the review and aggregation nodes.

Every system message starts with `/no_think` to disable Qwen3's chain-of-thought
mode — we trust the Pydantic structured output, so exposed reasoning wastes
tokens and latency without improving quality.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

FILE_REVIEW_SYSTEM = """/no_think
You are a senior Python engineer performing a rigorous code review.
Analyze the file as a whole and identify concrete issues (bugs, security,
performance, style, maintainability, missing tests) and genuine strengths.
Return your review strictly as a FileReview object matching the schema.
Do not include any commentary outside the structured output.

Guidelines:
- Only report real issues you can point to in the code.
- Prefer specific `line` numbers when applicable.
- `overall_score` reflects overall quality (0 worst, 10 best).
- Keep descriptions concise; suggestions must be actionable.
"""

FILE_REVIEW_HUMAN = """File: `{file_path}`

```python
{content}
```
"""

FILE_REVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", FILE_REVIEW_SYSTEM),
        ("human", FILE_REVIEW_HUMAN),
    ]
)


AGGREGATE_SYSTEM = """/no_think
You are a senior Python engineer synthesizing multiple per-file code reviews
into a repository-level summary. Return a RepoSummary that reflects the
aggregate state of the change set: overall assessment, total issues by
severity, top priorities to fix before merging, and general recommendations.

Guidelines:
- `overall_assessment` is one short paragraph.
- `top_priorities` and `recommendations` are actionable, not restatements
  of individual issues.
- Compute `total_issues_by_severity` accurately from the provided reviews.
"""

AGGREGATE_HUMAN = """Per-file reviews (JSON):

{reviews_json}
"""

AGGREGATE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", AGGREGATE_SYSTEM),
        ("human", AGGREGATE_HUMAN),
    ]
)
