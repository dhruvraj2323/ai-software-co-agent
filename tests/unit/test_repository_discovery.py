"""Unit tests for repository discovery service."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.security.path import WorkspaceEscapeError
from coagent.workspace.scope import WorkspaceScope


def test_discover_git_repository(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    git_dir = workspace_dir / ".git"
    git_dir.mkdir()

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    sub_dir = workspace_dir / "src" / "coagent"
    sub_dir.mkdir(parents=True)

    service = RepositoryDiscoveryService()
    repo_info = service.discover_repository(scope, start_path=sub_dir)

    assert repo_info.is_git_repository is True
    assert repo_info.root_path == workspace_dir.resolve()
    assert repo_info.relative_to_workspace == ""


def test_discover_non_git_repository(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "plain_workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    service = RepositoryDiscoveryService()
    repo_info = service.discover_repository(scope)

    assert repo_info.is_git_repository is False
    assert repo_info.root_path == workspace_dir.resolve()


def test_list_files_respects_ignores(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "repo"
    workspace_dir.mkdir()

    (workspace_dir / "main.py").write_text("print('hello')", encoding="utf-8")
    (workspace_dir / "test.pyc").write_text("bytecode", encoding="utf-8")

    venv_dir = workspace_dir / ".venv"
    venv_dir.mkdir()
    (venv_dir / "lib.py").write_text("lib", encoding="utf-8")

    git_dir = workspace_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("config", encoding="utf-8")

    src_dir = workspace_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("app", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    service = RepositoryDiscoveryService()
    files = service.list_files(scope)

    filenames = [f.name for f in files]
    assert "main.py" in filenames
    assert "app.py" in filenames
    assert "test.pyc" not in filenames
    assert "lib.py" not in filenames
    assert "config" not in filenames


def test_list_files_respects_gitignore(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "repo"
    workspace_dir.mkdir()

    (workspace_dir / ".gitignore").write_text("ignored_folder/\n*.secret\n", encoding="utf-8")
    (workspace_dir / "main.py").write_text("print('hello')", encoding="utf-8")
    (workspace_dir / "key.secret").write_text("secret", encoding="utf-8")

    sub_dir = workspace_dir / "ignored_folder"
    sub_dir.mkdir()
    (sub_dir / "data.txt").write_text("data", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    service = RepositoryDiscoveryService()
    files = service.list_files(scope)

    filenames = [f.name for f in files]
    assert "main.py" in filenames
    assert "key.secret" not in filenames
    assert "data.txt" not in filenames


def test_discover_rejects_out_of_workspace_start_path(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    service = RepositoryDiscoveryService()
    with pytest.raises(WorkspaceEscapeError):
        service.discover_repository(scope, start_path=outside_dir)

