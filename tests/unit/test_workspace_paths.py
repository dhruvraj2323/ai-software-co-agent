"""Unit tests for deterministic workspace path resolution."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from coagent.workspace import WorkspaceScope
from coagent.workspace.paths import resolve_workspace_path


def test_resolve_workspace_path_resolves_relative_path_from_scope_root(
    tmp_path: Path,
) -> None:
    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(tmp_path),
    )
    resolved = resolve_workspace_path(scope, "src/coagent/core")
    assert resolved == (tmp_path / "src/coagent/core").resolve()
def test_resolve_workspace_path_resolves_absolute_path_deterministically(
    tmp_path: Path,
) -> None:
    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(tmp_path),
    )
    absolute_path = tmp_path / "src" / "coagent"
    first = resolve_workspace_path(scope, str(absolute_path))
    second = resolve_workspace_path(scope, str(absolute_path))
    assert first == second
    assert first == absolute_path.resolve()
def test_resolve_workspace_path_normalizes_dot_segments(
    tmp_path: Path,
) -> None:
    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(tmp_path),
    )
    resolved = resolve_workspace_path(scope, "src/../tests")
    assert resolved == (tmp_path / "tests").resolve()
def test_resolve_workspace_path_does_not_use_current_working_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    current_directory = tmp_path / "other"
    current_directory.mkdir()
    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_root),
    )
    monkeypatch.chdir(current_directory)
    resolved = resolve_workspace_path(scope, "src")
    assert resolved == (workspace_root / "src").resolve()
    assert resolved != (current_directory / "src").resolve()
