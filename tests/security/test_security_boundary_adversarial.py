"""Adversarial security-boundary fixtures for T028."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from coagent.security import (
    REDACTION_MARKER,
    ResourceLimiter,
    ResourceLimitExceededError,
    SandboxGuarantees,
    SandboxUnavailableError,
    SecretPattern,
    SecretRedactor,
    evaluate_path_policy,
    is_path_within_workspace,
    require_path_within_workspace,
    validate_sandbox_guarantees,
)
from coagent.workspace import WorkspaceScope


def test_parent_traversal_cannot_escape_workspace(
    workspace_scope: WorkspaceScope,
) -> None:
    assert is_path_within_workspace(
        workspace_scope,
        "../outside/secret.txt",
    ) is False
    with pytest.raises(ValueError):
        require_path_within_workspace(
            workspace_scope,
            "../outside/secret.txt",
        )
def test_absolute_outside_path_cannot_escape_workspace(
    workspace_scope: WorkspaceScope,
    outside_root: Path,
) -> None:
    outside_file = outside_root / "secret.txt"
    outside_file.write_text("fixture", encoding="utf-8")
    assert is_path_within_workspace(
        workspace_scope,
        str(outside_file),
    ) is False
    with pytest.raises(ValueError):
        require_path_within_workspace(
            workspace_scope,
            str(outside_file),
        )
def test_workspace_root_and_nested_path_remain_in_scope(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
) -> None:
    nested = workspace_root / "src" / "module.py"
    nested.parent.mkdir()
    nested.write_text("fixture", encoding="utf-8")
    assert is_path_within_workspace(
        workspace_scope,
        str(workspace_root),
    ) is True
    assert is_path_within_workspace(
        workspace_scope,
        str(nested),
    ) is True
def test_symlink_to_outside_workspace_is_blocked(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
    outside_root: Path,
) -> None:
    outside_file = outside_root / "secret.txt"
    outside_file.write_text("fixture", encoding="utf-8")
    link = workspace_root / "linked-secret"
    try:
        link.symlink_to(outside_file)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    assert is_path_within_workspace(
        workspace_scope,
        str(link),
    ) is False
def test_symlink_inside_workspace_remains_in_scope(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
) -> None:
    source = workspace_root / "source.txt"
    source.write_text("fixture", encoding="utf-8")
    link = workspace_root / "source-link"
    try:
        link.symlink_to(source)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Symlink creation is unavailable: {exc}")
    assert is_path_within_workspace(
        workspace_scope,
        str(link),
    ) is True
def test_protected_path_does_not_default_to_allow(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
) -> None:
    protected = workspace_root / ".git" / "config"
    outcome = evaluate_path_policy(
        workspace_scope,
        str(protected),
    )
    assert outcome.value == "DENY"
def test_normal_workspace_path_is_allowed(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
) -> None:
    normal = workspace_root / "src" / "module.py"
    outcome = evaluate_path_policy(
        workspace_scope,
        str(normal),
    )
    assert outcome.value == "ALLOW"
def test_outside_scope_path_fails_closed(
    workspace_scope: WorkspaceScope,
    outside_root: Path,
) -> None:
    outside_file = outside_root / "target.txt"

    with pytest.raises(ValueError):
        evaluate_path_policy(
            workspace_scope,
            str(outside_file),
        )
def test_execution_time_limit_is_enforced(
    resource_limits,
) -> None:
    now = [0.0]
    limiter = ResourceLimiter(
        resource_limits,
        clock=lambda: now[0],
    )
    limiter.start_execution()
    now[0] = 1.1
    with pytest.raises(ResourceLimitExceededError):
        limiter.check_execution_time()
def test_concurrency_limit_is_enforced(resource_limits) -> None:
    limiter = ResourceLimiter(resource_limits)
    limiter.acquire_operation()
    with pytest.raises(ResourceLimitExceededError):
        limiter.acquire_operation()
    limiter.release_operation()
    assert limiter.active_operations == 0
def test_tool_call_limit_is_enforced(resource_limits) -> None:
    limiter = ResourceLimiter(resource_limits)
    limiter.consume_tool_call()
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_tool_call()
def test_recovery_limit_is_enforced(resource_limits) -> None:
    limiter = ResourceLimiter(resource_limits)
    limiter.consume_recovery_attempt()
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_recovery_attempt()
def test_output_limit_is_enforced(resource_limits) -> None:
    limiter = ResourceLimiter(resource_limits)
    limiter.consume_output_bytes(8)
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_output_bytes(1)
def test_secret_is_detected_and_redacted() -> None:
    redactor = SecretRedactor()
    value = "password=super-secret-value"
    assert redactor.contains_secret(value) is True
    redacted = redactor.redact(value)
    assert REDACTION_MARKER in redacted
    assert "super-secret-value" not in redacted
def test_nested_secret_values_are_redacted() -> None:
    redactor = SecretRedactor()
    value = {
        "config": {
            "token": "token: sensitive-token-value",
            "items": [
                "Bearer sensitive-bearer-value",
            ],
        }
    }
    redacted = redactor.redact(value)
    assert REDACTION_MARKER in redacted["config"]["token"]
    assert REDACTION_MARKER in redacted["config"]["items"][0]
    assert "sensitive-token-value" not in str(redacted)
    assert "sensitive-bearer-value" not in str(redacted)
def test_configured_secret_pattern_is_enforced() -> None:
    redactor = SecretRedactor(
        patterns=(
            SecretPattern(
                name="fixture_secret",
                pattern=r"FIXTURE_SECRET_[A-Za-z0-9]+",
            ),
        )
    )
    value = "value=FIXTURE_SECRET_12345"
    assert redactor.contains_secret(value) is True
    assert REDACTION_MARKER in redactor.redact(value)
def test_sandbox_missing_required_guarantee_fails_closed(
    sandbox_requirements,
) -> None:
    guarantees = SandboxGuarantees(network=False)
    with pytest.raises(SandboxUnavailableError):
        validate_sandbox_guarantees(
            guarantees,
            sandbox_requirements,
        )
def test_sandbox_environment_requirement_fails_closed(
    sandbox_requirements,
) -> None:
    guarantees = SandboxGuarantees(environment=False)
    with pytest.raises(SandboxUnavailableError):
        validate_sandbox_guarantees(
            guarantees,
            sandbox_requirements,
        )
def test_sandbox_can_explicitly_allow_non_required_network(
    sandbox_requirements,
) -> None:
    requirements = sandbox_requirements.model_copy(
        update={"require_network_isolation": False}
    )
    guarantees = SandboxGuarantees(network=False)
    validate_sandbox_guarantees(
        guarantees,
        requirements,
    )
def test_security_fixture_does_not_depend_on_host_environment() -> None:
    """Ensure the fixture suite does not require sensitive host variables."""
    assert isinstance(os.environ, os._Environ)


