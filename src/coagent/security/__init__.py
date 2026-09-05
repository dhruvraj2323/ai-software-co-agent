"""Security boundary primitives."""

from coagent.security.limits import (
    ResourceLimiter,
    ResourceLimitExceededError,
    ResourceLimits,
)
from coagent.security.path import (
    WorkspaceEscapeError,
    is_path_within_workspace,
    require_path_within_workspace,
)
from coagent.security.policy import (
    PathPolicyOutcome,
    ProtectedPathCategory,
    ProtectedPathPolicy,
    evaluate_path_policy,
    is_protected_path,
)

__all__ = [
    "PathPolicyOutcome",
    "ProtectedPathCategory",
    "ProtectedPathPolicy",
    "ResourceLimitExceededError",
    "ResourceLimiter",
    "ResourceLimits",
    "WorkspaceEscapeError",
    "evaluate_path_policy",
    "is_path_within_workspace",
    "is_protected_path",
    "require_path_within_workspace",
]
