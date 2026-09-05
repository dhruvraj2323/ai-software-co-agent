"""Protected workspace path policy."""
from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from coagent.security.path import (
    require_path_within_workspace,
)
from coagent.workspace import WorkspaceScope


class PathPolicyOutcome(StrEnum):
    """Default security outcome for a protected workspace target."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    ASK = "ASK"
    RESTRICT = "RESTRICT"
class ProtectedPathCategory(StrEnum):
    """Built-in protected-resource categories."""
    VCS = "VCS"
    SECRETS = "SECRETS"
    SECURITY = "SECURITY"
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"
    AUDIT = "AUDIT"
    CONFIGURATION = "CONFIGURATION"
class ProtectedPathPolicy:
    """Classify workspace paths against built-in and configured protections.
    T024 provides protected-resource policy primitives. Higher-level tool,
    risk, approval, and policy-engine evaluation remain outside this class.
    """
    _BUILTIN_RULES: tuple[tuple[ProtectedPathCategory, tuple[str, ...]], ...] = (
        (
            ProtectedPathCategory.VCS,
            (".git",),
        ),
        (
            ProtectedPathCategory.SECRETS,
            (
                ".env",
                ".env.*",
                "*.pem",
                "*.key",
                "*.p12",
                "*.pfx",
            ),
        ),
        (
            ProtectedPathCategory.SECURITY,
            (
                "security",
                ".security",
                "security-config",
            ),
        ),
        (
            ProtectedPathCategory.PRODUCTION,
            (
                "production",
                "prod",
                "deployment",
                "deploy",
            ),
        ),
        (
            ProtectedPathCategory.SANDBOX,
            (
                "sandbox",
                ".sandbox",
            ),
        ),
        (
            ProtectedPathCategory.AUDIT,
            (
                "audit",
                ".audit",
                "audit-logs",
                "security-evidence",
            ),
        ),
        (
            ProtectedPathCategory.CONFIGURATION,
            (
                "configs/security",
                "configs/policy",
                "policy.schema.json",
            ),
        ),
    )
    def __init__(self, additional_protected_paths: tuple[str, ...] = ()) -> None:
        """Create a policy with optional additional protected paths."""
        self._additional_protected_paths = tuple(
            Path(path).as_posix().strip("/")
            for path in additional_protected_paths
            if path
        )
    def classify(
        self,
        scope: WorkspaceScope,
        path: str,
    ) -> ProtectedPathCategory | None:
        """Return the protected category for a path, if one applies.
        The supplied path is first canonicalized and required to remain inside
        the authorized workspace. An out-of-scope path therefore fails closed.
        """
        resolved = require_path_within_workspace(scope, path)
        root = Path(scope.root).resolve()
        relative = resolved.relative_to(root)
        parts = relative.parts
        relative_posix = relative.as_posix()
        for category, patterns in self._BUILTIN_RULES:
            if self._matches(relative_posix, parts, patterns):
                return category
        if self._matches(
            relative_posix,
            parts,
            self._additional_protected_paths,
        ):
            return ProtectedPathCategory.CONFIGURATION
        return None
    def outcome(
        self,
        scope: WorkspaceScope,
        path: str,
    ) -> PathPolicyOutcome:
        """Return the default policy outcome for a protected target.
        T024 treats protected resources as denied by default. Higher-level
        policy evaluation may later impose stricter tool-specific behavior,
        but it must not weaken hard protection.
        """
        category = self.classify(scope, path)
        if category is not None:
            return PathPolicyOutcome.DENY
        return PathPolicyOutcome.ALLOW
    @staticmethod
    def _matches(
        relative_posix: str,
        parts: tuple[str, ...],
        patterns: tuple[str, ...],
    ) -> bool:
        """Match a relative path against protected path patterns."""
        for pattern in patterns:
            normalized = pattern.replace("\\", "/").strip("/")
            if not normalized:
                continue
            if relative_posix == normalized:
                return True
            if relative_posix.startswith(f"{normalized}/"):
                return True
            if any(
                Path(part).match(normalized)
                for part in parts
            ):
                return True
        return False
def is_protected_path(
    scope: WorkspaceScope,
    path: str,
    policy: ProtectedPathPolicy | None = None,
) -> bool:
    """Return whether a workspace path is protected."""
    active_policy = policy or ProtectedPathPolicy()
    return active_policy.classify(scope, path) is not None
def evaluate_path_policy(
    scope: WorkspaceScope,
    path: str,
    policy: ProtectedPathPolicy | None = None,
) -> PathPolicyOutcome:
    """Return the T024 default outcome for a workspace path."""
    active_policy = policy or ProtectedPathPolicy()
    return active_policy.outcome(scope, path)
