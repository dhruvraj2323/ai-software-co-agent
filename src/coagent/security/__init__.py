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
from coagent.security.secrets import (
    REDACTION_MARKER,
    SecretPattern,
    SecretRedactor,
    contains_secret,
    redact_secrets,
)

__all__ = [
    "PathPolicyOutcome",
    "ProtectedPathCategory",
    "ProtectedPathPolicy",
    "REDACTION_MARKER",
    "ResourceLimitExceededError",
    "ResourceLimiter",
    "ResourceLimits",
    "SecretPattern",
    "SecretRedactor",
    "WorkspaceEscapeError",
    "contains_secret",
    "evaluate_path_policy",
    "is_path_within_workspace",
    "is_protected_path",
    "redact_secrets",
    "require_path_within_workspace",
]
