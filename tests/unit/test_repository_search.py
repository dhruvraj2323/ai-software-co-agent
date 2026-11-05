"""Unit tests for repository search adapter."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.repository.search import RepositorySearchAdapter
from coagent.security.path import WorkspaceEscapeError
from coagent.workspace.scope import WorkspaceScope


def test_find_files_pattern(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    (workspace_dir / "test_a.py").write_text("# a", encoding="utf-8")
    (workspace_dir / "test_b.py").write_text("# b", encoding="utf-8")
    (workspace_dir / "main.py").write_text("# main", encoding="utf-8")
    (workspace_dir / "notes.txt").write_text("# notes", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()
    results = searcher.find_files(scope, "test_*.py")

    names = [r.name for r in results]
    assert "test_a.py" in names
    assert "test_b.py" in names
    assert "main.py" not in names
    assert "notes.txt" not in names


def test_search_content_literal_and_regex(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    file1 = workspace_dir / "service.py"
    file1.write_text(
        "class OrderService:\n    def process_order(self, order_id: str):\n        return True\n",
        encoding="utf-8",
    )

    file2 = workspace_dir / "utils.py"
    file2.write_text(
        "def helper():\n    # order processing helper\n    pass\n",
        encoding="utf-8",
    )

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()

    # Literal search
    res = searcher.search_content(scope, "process_order")
    assert res.total_matches == 1
    assert res.matches[0].line_number == 2
    assert "def process_order" in res.matches[0].line_content

    # Regex search
    res_regex = searcher.search_content(scope, r"def \w+\(self", is_regex=True)
    assert res_regex.total_matches == 1
    assert "process_order" in res_regex.matches[0].line_content


def test_search_content_filters_secrets(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    secret_env = workspace_dir / ".env"
    secret_env.write_text("API_SECRET_KEY=supersecret123\n", encoding="utf-8")

    normal_file = workspace_dir / "config.py"
    normal_file.write_text("DEFAULT_TIMEOUT = 30\n", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()
    res = searcher.search_content(scope, "supersecret123")
    assert res.total_matches == 0  # .env is a secret file and excluded from search content


def test_search_rejects_subpath_outside_workspace(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()
    with pytest.raises(WorkspaceEscapeError):
        searcher.search_content(scope, "query", subpath=outside_dir)

