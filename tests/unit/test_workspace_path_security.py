"""Unit tests for workspace traversal and symlink escape protection."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.security import (
    WorkspaceEscapeError,
    is_path_within_workspace,
    require_path_within_workspace,
)
from coagent.workspace import WorkspaceScope


def make_scope(root: Path) -> WorkspaceScope:
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(root),
    )
def test_parent_traversal_outside_workspace_is_blocked(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    scope = make_scope(workspace_root)
    assert not is_path_within_workspace(scope, "../outside")
def test_parent_traversal_outside_workspace_raises(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    scope = make_scope(workspace_root)
    with pytest.raises(WorkspaceEscapeError):
        require_path_within_workspace(scope, "../outside")
def test_absolute_path_outside_workspace_is_blocked(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    outside_path = tmp_path / "outside"
    outside_path.mkdir()
    scope = make_scope(workspace_root)
    assert not is_path_within_workspace(scope, str(outside_path))
def test_nested_path_inside_workspace_is_allowed(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    nested = workspace_root / "src" / "coagent"
    nested.mkdir(parents=True)
    scope = make_scope(workspace_root)
    assert is_path_within_workspace(scope, "src/coagent")
def test_absolute_path_inside_workspace_is_allowed(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    nested = workspace_root / "src"
    nested.mkdir(parents=True)
    scope = make_scope(workspace_root)
    assert is_path_within_workspace(scope, str(nested))
def test_symlink_to_outside_workspace_is_blocked(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    outside_file = outside_root / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    link = workspace_root / "linked-secret"
    try:
        link.symlink_to(outside_file)
    except OSError as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    scope = make_scope(workspace_root)
    assert not is_path_within_workspace(scope, "linked-secret")
def test_symlink_to_outside_workspace_raises(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    outside_file = outside_root / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    link = workspace_root / "linked-secret"
    try:
        link.symlink_to(outside_file)
    except OSError as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    scope = make_scope(workspace_root)
    with pytest.raises(WorkspaceEscapeError):
        require_path_within_workspace(scope, "linked-secret")
def test_symlink_to_inside_workspace_is_allowed(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    target = workspace_root / "src"
    target.mkdir()
    link = workspace_root / "source-link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    scope = make_scope(workspace_root)
    assert is_path_within_workspace(scope, "source-link")
def test_workspace_root_itself_is_allowed(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    scope = make_scope(workspace_root)
    assert require_path_within_workspace(scope, ".") == workspace_root.resolve()
def test_directory_junction_to_outside_workspace_is_blocked(
    tmp_path: Path,
) -> None:
    """A Windows directory junction must not bypass workspace containment."""
    if sys.platform != "win32":
        pytest.skip("Windows junction test")
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    outside_file = outside_root / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    junction = workspace_root / "outside-link"
    result = subprocess.run(
        [
            "cmd",
            "/c",
            "mklink",
            "/J",
            str(junction),
            str(outside_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(
            f"Directory junction creation unavailable: {result.stderr.strip()}"
        )
    scope = make_scope(workspace_root)
    assert not is_path_within_workspace(
        scope,
        "outside-link/secret.txt",
    )
    with pytest.raises(WorkspaceEscapeError):
        require_path_within_workspace(
            scope,
            "outside-link/secret.txt",
        )
