import pytest
from pydantic import ValidationError

from ai_code_review_agent.models import (
    FileReview,
    Issue,
    RepoSummary,
    SeverityCounts,
)


class TestIssue:
    def test_valid_issue(self):
        issue = Issue(
            category="bug",
            severity="high",
            line=42,
            description="Off-by-one in the loop bound.",
            suggestion="Change `<` to `<=`.",
        )
        assert issue.line == 42
        assert issue.category == "bug"
        assert issue.severity == "high"

    def test_line_is_optional(self):
        issue = Issue(
            category="style",
            severity="low",
            description="Missing module docstring.",
            suggestion="Add a top-level docstring.",
        )
        assert issue.line is None

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            Issue(
                category="not-a-category",
                severity="low",
                description="x",
                suggestion="y",
            )

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValidationError):
            Issue(
                category="bug",
                severity="urgent",
                description="x",
                suggestion="y",
            )

    def test_line_must_be_positive(self):
        with pytest.raises(ValidationError):
            Issue(
                category="bug",
                severity="low",
                line=0,
                description="x",
                suggestion="y",
            )


class TestFileReview:
    def test_defaults_are_empty_lists(self):
        review = FileReview(
            file_path="src/foo.py",
            overall_score=8.5,
            summary="Well-structured module.",
        )
        assert review.issues == []
        assert review.strengths == []

    def test_score_upper_bound(self):
        with pytest.raises(ValidationError):
            FileReview(file_path="x.py", overall_score=10.1, summary="x")

    def test_score_lower_bound(self):
        with pytest.raises(ValidationError):
            FileReview(file_path="x.py", overall_score=-0.1, summary="x")

    def test_accepts_issues_and_strengths(self):
        review = FileReview(
            file_path="x.py",
            overall_score=7.0,
            summary="OK",
            issues=[
                Issue(
                    category="performance",
                    severity="medium",
                    description="Loop rebuilds a list on each call.",
                    suggestion="Cache the result.",
                )
            ],
            strengths=["Clear naming.", "Good test coverage."],
        )
        assert len(review.issues) == 1
        assert review.strengths[0] == "Clear naming."


class TestSeverityCounts:
    def test_defaults_to_zero(self):
        counts = SeverityCounts()
        assert (counts.low, counts.medium, counts.high, counts.critical) == (0, 0, 0, 0)

    def test_rejects_negative(self):
        with pytest.raises(ValidationError):
            SeverityCounts(low=-1)


class TestRepoSummary:
    def test_defaults(self):
        summary = RepoSummary(overall_assessment="Ready to merge.")
        assert summary.total_issues_by_severity == SeverityCounts()
        assert summary.top_priorities == []
        assert summary.recommendations == []

    def test_accepts_populated_fields(self):
        summary = RepoSummary(
            overall_assessment="Needs work.",
            total_issues_by_severity=SeverityCounts(low=2, high=1),
            top_priorities=["Fix SQL injection in handler."],
            recommendations=["Add integration tests."],
        )
        assert summary.total_issues_by_severity.high == 1
        assert summary.top_priorities == ["Fix SQL injection in handler."]
