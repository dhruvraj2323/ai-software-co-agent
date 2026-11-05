"""Security tests for repository intelligence boundary and scope containment (T054)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.index import RepositoryIndex
from coagent.repository.search import RepositorySearchAdapter
from coagent.security.path import WorkspaceEscapeError
from coagent.workspace.scope import WorkspaceScope


def test_discovery_never_escapes_to_parent_git(tmp_path: Path) -> None:
    """If parent folder has .git, discovery inside subfolder must NOT return parent folder."""
    parent_dir = tmp_path / "outer"
    parent_dir.mkdir()
    (parent_dir / ".git").mkdir()

    workspace_dir = parent_dir / "workspace"
    workspace_dir.mkdir()
    (workspace_dir / "file.txt").write_text("inside", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    discovery = RepositoryDiscoveryService()
    repo_info = discovery.discover_repository(scope)

    # Must be bounded strictly by workspace_dir, NOT parent_dir
    assert repo_info.root_path == workspace_dir.resolve()
    assert repo_info.is_git_repository is False


def test_search_rejects_path_traversal(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    (workspace_dir / "file.txt").write_text("inside", encoding="utf-8")

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").write_text("CLASSIFIED", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()

    with pytest.raises(WorkspaceEscapeError):
        searcher.search_content(scope, "CLASSIFIED", subpath="../outside")

    with pytest.raises(WorkspaceEscapeError):
        searcher.search_content(scope, "CLASSIFIED", subpath=str(outside_dir))


def test_search_never_exposes_secrets(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    access_val = "AKIA" + "1234567890ABCDEF"
    (workspace_dir / ".env").write_text("AWS_SECRET_KEY=" + access_val + "\n", encoding="utf-8")
    key_pem = (
        "-----BEGIN " + "PRIVATE KEY-----\n"
        "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQD0Z\n"
    )
    (workspace_dir / "server.key").write_text(key_pem, encoding="utf-8")
    (workspace_dir / "normal.py").write_text("print('safe')", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    searcher = RepositorySearchAdapter()

    res_aws = searcher.search_content(scope, access_val)
    assert res_aws.total_matches == 0

    res_key = searcher.search_content(scope, "BEGIN " + "PRIVATE KEY")
    assert res_key.total_matches == 0


def test_index_is_fresh_rejects_out_of_workspace_path(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.py").write_text("x = 1", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    index = RepositoryIndex()
    with pytest.raises(WorkspaceEscapeError):
        index.is_fresh(scope, str(outside_dir / "secret.py"))

    index.close()
