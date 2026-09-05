"""Deterministic workspace path resolution."""
from __future__ import annotations

from pathlib import Path

from coagent.workspace.scope import WorkspaceScope


def resolve_workspace_path(scope: WorkspaceScope, path: str) -> Path:
    """Resolve a path against the explicitly declared workspace root.
    Relative paths are resolved from the workspace scope root. Absolute paths
    remain absolute candidates. This function performs canonical resolution
    only; authorization and escape protection belong to later security tasks.
    """
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path(scope.root) / candidate
    return candidate.resolve()
