import subprocess
from pathlib import Path

import pytest

from ai_code_review_agent.tools.git_tools import (
    get_repo_name,
    list_changed_python_files,
    read_file_at_ref,
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "myrepo"
    r.mkdir()
    _git(r, "init", "-b", "main")
    _git(r, "config", "user.email", "test@example.com")
    _git(r, "config", "user.name", "Test")
    _git(r, "config", "commit.gpgsign", "false")
    return r


class TestListChangedPythonFiles:
    def test_lists_added_and_modified_py_files(self, repo: Path):
        (repo / "a.py").write_text("print('a')\n")
        (repo / "b.txt").write_text("not python\n")
        _commit(repo, "initial")
        base = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "a.py").write_text("print('a modified')\n")
        (repo / "c.py").write_text("print('c')\n")
        (repo / "d.md").write_text("markdown\n")
        _commit(repo, "second")

        changed = list_changed_python_files(str(repo), base, "HEAD")
        assert set(changed) == {"a.py", "c.py"}

    def test_excludes_deleted_files(self, repo: Path):
        (repo / "keep.py").write_text("x\n")
        (repo / "gone.py").write_text("y\n")
        _commit(repo, "initial")
        base = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "gone.py").unlink()
        (repo / "new.py").write_text("z\n")
        _commit(repo, "second")

        changed = list_changed_python_files(str(repo), base, "HEAD")
        assert "gone.py" not in changed
        assert "new.py" in changed

    def test_returns_empty_when_no_python_changes(self, repo: Path):
        (repo / "a.py").write_text("print('a')\n")
        _commit(repo, "initial")
        base = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "readme.md").write_text("hi\n")
        _commit(repo, "docs only")

        assert list_changed_python_files(str(repo), base, "HEAD") == []


class TestReadFileAtRef:
    def test_reads_exact_content(self, repo: Path):
        (repo / "x.py").write_text("hello\nworld\n")
        _commit(repo, "initial")
        assert read_file_at_ref(str(repo), "x.py", "HEAD") == "hello\nworld\n"

    def test_reads_historical_version(self, repo: Path):
        (repo / "x.py").write_text("v1\n")
        _commit(repo, "initial")
        old = _git(repo, "rev-parse", "HEAD").strip()

        (repo / "x.py").write_text("v2\n")
        _commit(repo, "second")

        assert read_file_at_ref(str(repo), "x.py", old) == "v1\n"
        assert read_file_at_ref(str(repo), "x.py", "HEAD") == "v2\n"


class TestGetRepoName:
    def test_falls_back_to_directory_name(self, repo: Path):
        assert get_repo_name(str(repo)) == "myrepo"

    def test_uses_https_remote_url(self, repo: Path):
        _git(
            repo,
            "remote",
            "add",
            "origin",
            "https://github.com/user/awesome-repo.git",
        )
        assert get_repo_name(str(repo)) == "awesome-repo"

    def test_uses_ssh_remote_url(self, repo: Path):
        _git(repo, "remote", "add", "origin", "git@github.com:user/proj.git")
        assert get_repo_name(str(repo)) == "proj"

    def test_handles_url_without_git_suffix(self, repo: Path):
        _git(repo, "remote", "add", "origin", "https://gitlab.com/user/thing")
        assert get_repo_name(str(repo)) == "thing"
