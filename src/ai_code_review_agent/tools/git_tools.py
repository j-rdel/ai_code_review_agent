"""Git-related utilities used by graph nodes."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo_path: str | Path, *args: str) -> str:
    """Run a git command in `repo_path` and return stdout as text."""
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def list_changed_python_files(
    repo_path: str | Path, base_ref: str, head_ref: str
) -> list[str]:
    """Return relative paths of `.py` files changed between two refs.

    Deletions are excluded — reviewing a deleted file makes no sense.
    Includes Added, Copied, Modified, Renamed and Type-changed entries.
    """
    output = _run_git(
        repo_path,
        "diff",
        "--name-only",
        "--diff-filter=ACMRT",
        f"{base_ref}..{head_ref}",
        "--",
        "*.py",
    )
    return [line for line in output.splitlines() if line]


def read_file_at_ref(repo_path: str | Path, path: str, ref: str) -> str:
    """Return the contents of `path` as seen at `ref`."""
    return _run_git(repo_path, "show", f"{ref}:{path}")


def get_repo_name(repo_path: str | Path) -> str:
    """Return a slug identifying the repository.

    Prefers the origin remote URL (stripping `.git`); falls back to the
    absolute directory name if no remote is configured.
    """
    try:
        url = _run_git(repo_path, "config", "--get", "remote.origin.url").strip()
    except subprocess.CalledProcessError:
        url = ""
    if url:
        name = url.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        if name:
            return name
    return Path(repo_path).resolve().name
