"""Security boundary primitives."""
from coagent.security.path import (
    WorkspaceEscapeError,
    is_path_within_workspace,
    require_path_within_workspace,
)

__all__ = [
    "WorkspaceEscapeError",
    "is_path_within_workspace",
    "require_path_within_workspace",
]
