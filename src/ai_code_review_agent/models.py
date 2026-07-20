"""Pydantic schemas for structured LLM output."""

from typing import Literal

from pydantic import BaseModel, Field

IssueCategory = Literal[
    "bug",
    "security",
    "performance",
    "style",
    "maintainability",
    "test",
]

Severity = Literal["low", "medium", "high", "critical"]


class Issue(BaseModel):
    """A single issue identified in a code file."""

    category: IssueCategory = Field(
        description="Category of the issue."
    )
    severity: Severity = Field(
        description="Severity of the issue."
    )
    line: int | None = Field(
        default=None,
        ge=1,
        description="1-based line number where the issue was found, when applicable.",
    )
    description: str = Field(
        description="Concise description of the issue."
    )
    suggestion: str = Field(
        description="Concrete suggestion to resolve the issue."
    )


class FileReview(BaseModel):
    """Review of a single Python file."""

    file_path: str = Field(
        description="Repository-relative path of the reviewed file."
    )
    overall_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall quality score from 0 (worst) to 10 (best).",
    )
    summary: str = Field(
        description="One-paragraph summary of the file's overall quality."
    )
    issues: list[Issue] = Field(
        default_factory=list,
        description="Issues identified in the file.",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Positive aspects and good practices found in the file.",
    )


class SeverityCounts(BaseModel):
    """Total count of issues per severity across all reviewed files."""

    low: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    high: int = Field(default=0, ge=0)
    critical: int = Field(default=0, ge=0)


class RepoSummary(BaseModel):
    """Aggregated review across all changed files in the repository."""

    overall_assessment: str = Field(
        description="High-level assessment of the change set as a whole."
    )
    total_issues_by_severity: SeverityCounts = Field(
        default_factory=SeverityCounts,
        description="Count of issues found across all files, grouped by severity.",
    )
    top_priorities: list[str] = Field(
        default_factory=list,
        description="Most important issues that should be addressed before merging.",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="General recommendations for the change set.",
    )
