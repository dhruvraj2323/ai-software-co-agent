"""Fail-closed security-control tests for T029."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from coagent.security import (
    ResourceLimiter,
    ResourceLimitExceededError,
    SandboxGuarantees,
    SandboxUnavailableError,
    is_path_within_workspace,
    validate_sandbox_guarantees,
)
from coagent.workspace import WorkspaceScope


def require_privileged_action_controls(
    scope: WorkspaceScope,
    target: str,
    limiter: ResourceLimiter,
    guarantees: SandboxGuarantees,
    *,
    requirements,
    action: Callable[[], None],
) -> None:
    """Require all existing security controls before a privileged action."""
    if not is_path_within_workspace(scope, target):
        raise ValueError("privileged action blocked by workspace scope")
    limiter.check_execution_time()
    validate_sandbox_guarantees(
        guarantees,
        requirements,
    )
    action()
def test_privileged_action_requires_all_security_controls(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
    resource_limits,
    sandbox_requirements,
) -> None:
    """A valid privileged action requires every security control to pass."""
    target = workspace_root / "allowed.txt"
    limiter = ResourceLimiter(resource_limits)
    limiter.start_execution()
    action_ran = False
    def action() -> None:
        nonlocal action_ran
        action_ran = True
        target.write_text("fixture", encoding="utf-8")
    require_privileged_action_controls(
        workspace_scope,
        str(target),
        limiter,
        SandboxGuarantees(),
        requirements=sandbox_requirements,
        action=action,
    )
    assert action_ran is True
    assert target.exists() is True
def test_privileged_action_blocks_on_workspace_control_failure(
    workspace_scope: WorkspaceScope,
    outside_root: Path,
    resource_limits,
    sandbox_requirements,
) -> None:
    """A workspace failure must block the privileged action."""
    target = outside_root / "outside.txt"
    limiter = ResourceLimiter(resource_limits)
    limiter.start_execution()
    action_ran = False
    def action() -> None:
        nonlocal action_ran
        action_ran = True
        target.write_text("must-not-run", encoding="utf-8")
    with pytest.raises(ValueError, match="workspace scope"):
        require_privileged_action_controls(
            workspace_scope,
            str(target),
            limiter,
            SandboxGuarantees(),
            requirements=sandbox_requirements,
            action=action,
        )
    assert action_ran is False
    assert target.exists() is False
def test_privileged_action_blocks_on_resource_control_failure(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
    resource_limits,
    sandbox_requirements,
) -> None:
    """An expired execution budget must block the privileged action."""
    target = workspace_root / "allowed.txt"
    now = [0.0]
    limiter = ResourceLimiter(
        resource_limits,
        clock=lambda: now[0],
    )
    limiter.start_execution()
    now[0] = resource_limits.max_execution_seconds + 0.1
    action_ran = False
    def action() -> None:
        nonlocal action_ran
        action_ran = True
        target.write_text("must-not-run", encoding="utf-8")
    with pytest.raises(ResourceLimitExceededError, match="execution time"):
        require_privileged_action_controls(
            workspace_scope,
            str(target),
            limiter,
            SandboxGuarantees(),
            requirements=sandbox_requirements,
            action=action,
        )
    assert action_ran is False
    assert target.exists() is False
def test_privileged_action_blocks_on_sandbox_control_failure(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
    resource_limits,
    sandbox_requirements,
) -> None:
    """Missing sandbox guarantees must block the privileged action."""
    target = workspace_root / "allowed.txt"
    limiter = ResourceLimiter(resource_limits)
    limiter.start_execution()
    guarantees = SandboxGuarantees(workspace=False)
    action_ran = False
    def action() -> None:
        nonlocal action_ran
        action_ran = True
        target.write_text("must-not-run", encoding="utf-8")
    with pytest.raises(
        SandboxUnavailableError,
        match="required sandbox guarantees",
    ):
        require_privileged_action_controls(
            workspace_scope,
            str(target),
            limiter,
            guarantees,
            requirements=sandbox_requirements,
            action=action,
        )
    assert action_ran is False
    assert target.exists() is False
def test_privileged_action_does_not_continue_after_resource_failure(
    workspace_scope: WorkspaceScope,
    workspace_root: Path,
    resource_limits,
    sandbox_requirements,
) -> None:
    """A failed security control prevents the protected action from running."""
    target = workspace_root / "must-not-be-created.txt"
    now = [0.0]
    limiter = ResourceLimiter(
        resource_limits,
        clock=lambda: now[0],
    )
    limiter.start_execution()
    now[0] = resource_limits.max_execution_seconds + 0.1
    action_ran = False
    def action() -> None:
        nonlocal action_ran
        action_ran = True
        target.write_text("must-not-run", encoding="utf-8")
    with pytest.raises(ResourceLimitExceededError):
        require_privileged_action_controls(
            workspace_scope,
            str(target),
            limiter,
            SandboxGuarantees(),
            requirements=sandbox_requirements,
            action=action,
        )
    assert action_ran is False
    assert target.exists() is False
