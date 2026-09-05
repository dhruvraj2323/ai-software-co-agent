"""Workspace path containment enforcement."""
from __future__ import annotations

from pathlib import Path

from coagent.workspace import WorkspaceScope
from coagent.workspace.paths import resolve_workspace_path


class WorkspaceEscapeError(ValueError):
    """Raised when a resolved path is outside the authorized workspace."""
def is_path_within_workspace(scope: WorkspaceScope, path: str) -> bool:
    """Return whether a canonical path remains inside the authorized workspace."""
    root = Path(scope.root).resolve()
    resolved = resolve_workspace_path(scope, path)
    try:
        resolved.relative_to(root)
    except ValueError:
        return False
    return True
def require_path_within_workspace(scope: WorkspaceScope, path: str) -> Path:
    """Resolve and require that a path remains inside the authorized workspace."""
    root = Path(scope.root).resolve()
    resolved = resolve_workspace_path(scope, path)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkspaceEscapeError(
            f"Path is outside the authorized workspace: {resolved}"
        ) from exc
    return resolved
