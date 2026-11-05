"""Unit tests for Git adapter (T045)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from coagent.git.adapter import GitAdapter


def init_git_repo(path: Path) -> GitAdapter:
    """Initialize a mock local git repo for testing."""
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )
    return GitAdapter(path)


def test_non_git_directory_handled_gracefully(tmp_path: Path) -> None:
    non_git = tmp_path / "nongit"
    non_git.mkdir()
    adapter = GitAdapter(non_git)

    assert adapter.is_git_repository() is False
    status = adapter.get_status()
    assert status.is_clean is True
    assert adapter.get_diff() == ""


def test_git_status_and_diff_tracking(tmp_path: Path) -> None:
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    adapter = init_git_repo(repo_dir)

    assert adapter.is_git_repository() is True

    # Initial commit
    readme = repo_dir / "README.md"
    readme.write_text("# Initial\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo_dir), check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), check=True)

    status = adapter.get_status()
    assert status.is_clean is True

    # Modify file
    readme.write_text("# Updated\n", encoding="utf-8")
    status_dirty = adapter.get_status()
    assert status_dirty.is_clean is False
    assert "README.md" in status_dirty.modified_files

    diff = adapter.get_diff()
    assert "-# Initial" in diff
    assert "+# Updated" in diff

    # Rollback
    assert adapter.rollback() is True
    assert adapter.get_status().is_clean is True
    assert readme.read_text(encoding="utf-8") == "# Initial\n"
