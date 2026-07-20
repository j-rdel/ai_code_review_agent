"""Typer CLI entrypoint. Registered as `review` in `pyproject.toml`."""

from __future__ import annotations

from pathlib import Path

import typer

from ai_code_review_agent.config import settings
from ai_code_review_agent.graph import build_graph

app = typer.Typer(add_completion=False, help="AI-powered Python code review agent.")


@app.callback(invoke_without_command=True)
def main(
    repo: Path = typer.Option(
        Path("."),
        "--repo",
        "-r",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Path to the git repository to review.",
    ),
    base: str = typer.Option(
        settings.default_base_ref,
        "--base",
        "-b",
        help="Base git ref to diff from.",
    ),
    head: str = typer.Option(
        settings.default_head_ref,
        "--head",
        "-H",
        help="Head git ref to diff to.",
    ),
    out: Path = typer.Option(
        Path(settings.default_output_dir),
        "--out",
        "-o",
        file_okay=False,
        dir_okay=True,
        help="Directory to write the Markdown report into.",
    ),
) -> None:
    """Review Python changes between two git refs and write a Markdown report."""
    typer.echo(f"Reviewing {repo.resolve()} — {base}..{head}")
    graph = build_graph()
    final = graph.invoke(
        {
            "repo_path": str(repo.resolve()),
            "base_ref": base,
            "head_ref": head,
            "output_dir": str(out.resolve()),
            "file_reviews": [],
        }
    )
    n_files = len(final.get("file_reviews", []))
    typer.echo(f"Reviewed {n_files} file(s).")
    typer.echo(f"Report written: {final['report_path']}")
