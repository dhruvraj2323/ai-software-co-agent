"""Unit tests for the T024 protected-path policy."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.security import (
    PathPolicyOutcome,
    ProtectedPathCategory,
    ProtectedPathPolicy,
    WorkspaceEscapeError,
    evaluate_path_policy,
    is_protected_path,
)
from coagent.workspace import WorkspaceScope


def make_scope(root: Path) -> WorkspaceScope:
    """Create a workspace scope for a test root."""
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(root),
    )
def test_git_directory_is_protected(tmp_path: Path) -> None:
    """VCS internals are protected."""
    root = tmp_path / "workspace"
    (root / ".git").mkdir(parents=True)
    scope = make_scope(root)
    assert ProtectedPathPolicy().classify(scope, ".git") == ProtectedPathCategory.VCS
    assert is_protected_path(scope, ".git")
def test_nested_git_path_is_protected(tmp_path: Path) -> None:
    """Paths below VCS internals remain protected."""
    root = tmp_path / "workspace"
    (root / ".git" / "objects").mkdir(parents=True)
    scope = make_scope(root)
    assert (
        ProtectedPathPolicy().classify(scope, ".git/objects")
        == ProtectedPathCategory.VCS
    )
@pytest.mark.parametrize(
    "path",
    [
        ".env",
        ".env.local",
        "credentials.pem",
        "private.key",
    ],
)
def test_secret_files_are_protected(tmp_path: Path, path: str) -> None:
    """Credential and secret file patterns are protected."""
    root = tmp_path / "workspace"
    root.mkdir()
    scope = make_scope(root)
    assert (
        ProtectedPathPolicy().classify(scope, path)
        == ProtectedPathCategory.SECRETS
    )
@pytest.mark.parametrize(
    "path",
    [
        "security",
        ".security",
        "security-config",
    ],
)
def test_security_paths_are_protected(tmp_path: Path, path: str) -> None:
    """Security configuration areas are protected."""
    root = tmp_path / "workspace"
    (root / path).mkdir(parents=True)
    scope = make_scope(root)
    assert (
        ProtectedPathPolicy().classify(scope, path)
        == ProtectedPathCategory.SECURITY
    )
@pytest.mark.parametrize(
    "path",
    [
        "production",
        "prod",
        "deployment",
        "deploy",
    ],
)
def test_production_paths_are_protected(tmp_path: Path, path: str) -> None:
    """Production and deployment resources are protected."""
    root = tmp_path / "workspace"
    (root / path).mkdir(parents=True)
    scope = make_scope(root)
    assert (
        ProtectedPathPolicy().classify(scope, path)
        == ProtectedPathCategory.PRODUCTION
    )
def test_audit_path_is_protected(tmp_path: Path) -> None:
    """Audit and security evidence are protected."""
    root = tmp_path / "workspace"
    (root / "audit").mkdir(parents=True)
    scope = make_scope(root)
    assert (
        ProtectedPathPolicy().classify(scope, "audit")
        == ProtectedPathCategory.AUDIT
    )
def test_normal_source_path_is_not_protected(tmp_path: Path) -> None:
    """Ordinary workspace paths remain unprotected by T024."""
    root = tmp_path / "workspace"
    (root / "src" / "coagent").mkdir(parents=True)
    scope = make_scope(root)
    assert ProtectedPathPolicy().classify(scope, "src/coagent") is None
    assert not is_protected_path(scope, "src/coagent")
def test_configured_protected_path_is_protected(tmp_path: Path) -> None:
    """Additional protected paths can be configured."""
    root = tmp_path / "workspace"
    (root / "internal").mkdir(parents=True)
    scope = make_scope(root)
    policy = ProtectedPathPolicy(("internal",))
    assert policy.classify(scope, "internal") == ProtectedPathCategory.CONFIGURATION
def test_protected_path_default_outcome_is_deny(tmp_path: Path) -> None:
    """Protected targets fail closed by default."""
    root = tmp_path / "workspace"
    (root / ".git").mkdir(parents=True)
    scope = make_scope(root)
    assert evaluate_path_policy(scope, ".git") == PathPolicyOutcome.DENY
def test_normal_path_default_outcome_is_allow(tmp_path: Path) -> None:
    """Normal paths receive the ordinary default outcome."""
    root = tmp_path / "workspace"
    (root / "src").mkdir(parents=True)
    scope = make_scope(root)
    assert evaluate_path_policy(scope, "src") == PathPolicyOutcome.ALLOW
def test_outside_path_fails_closed(tmp_path: Path) -> None:
    """An out-of-scope path cannot be evaluated as an allowed target."""
    root = tmp_path / "workspace"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    scope = make_scope(root)
    with pytest.raises(WorkspaceEscapeError):
        evaluate_path_policy(scope, str(outside))
