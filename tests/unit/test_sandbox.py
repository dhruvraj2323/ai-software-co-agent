"""Unit tests for T027 sandbox interface and guarantee contracts."""
from __future__ import annotations

from uuid import uuid4

import pytest

from coagent.security import (
    ResourceLimits,
    SandboxGuarantee,
    SandboxGuarantees,
    SandboxRequirements,
    SandboxUnavailableError,
    require_sandbox_guarantees,
    validate_sandbox_guarantees,
)
from coagent.workspace import WorkspaceScope


def make_requirements() -> SandboxRequirements:
    """Create explicit sandbox requirements for tests."""
    return SandboxRequirements(
        workspace=WorkspaceScope(
            task_id=uuid4(),
            workspace_id=uuid4(),
            root="workspace",
        ),
        resource_limits=ResourceLimits(
            max_execution_seconds=30.0,
            max_concurrent_operations=2,
            max_tool_calls=10,
            max_recovery_attempts=3,
            max_output_bytes=4096,
        ),
    )
def test_requirements_require_explicit_workspace_and_limits() -> None:
    requirements = make_requirements()
    assert requirements.workspace.root == "workspace"
    assert requirements.resource_limits.max_execution_seconds == 30.0
def test_requirements_reject_unknown_fields() -> None:
    with pytest.raises(ValueError):
        SandboxRequirements(
            workspace=WorkspaceScope(
                task_id=uuid4(),
                workspace_id=uuid4(),
                root="workspace",
            ),
            resource_limits=ResourceLimits(
                max_execution_seconds=30.0,
                max_concurrent_operations=2,
                max_tool_calls=10,
                max_recovery_attempts=3,
                max_output_bytes=4096,
            ),
            unexpected="value",
        )
def test_full_guarantees_satisfy_requirements() -> None:
    requirements = make_requirements()
    guarantees = SandboxGuarantees()
    assert guarantees.supports(requirements) is True
@pytest.mark.parametrize(
    "guarantee",
    [
        SandboxGuarantee.WORKSPACE,
        SandboxGuarantee.NETWORK,
        SandboxGuarantee.ENVIRONMENT,
        SandboxGuarantee.TIMEOUT,
        SandboxGuarantee.OUTPUT,
        SandboxGuarantee.CONCURRENCY,
    ],
)
def test_guarantee_names_are_stable(guarantee: SandboxGuarantee) -> None:
    assert guarantee.value == guarantee.name
@pytest.mark.parametrize(
    "field",
    [
        "workspace",
        "network",
        "environment",
        "timeout",
        "output",
        "concurrency",
    ],
)
def test_missing_guarantee_fails_closed(field: str) -> None:
    requirements = make_requirements()
    guarantees = SandboxGuarantees().model_copy(update={field: False})
    assert guarantees.supports(requirements) is False
    with pytest.raises(SandboxUnavailableError):
        validate_sandbox_guarantees(guarantees, requirements)
def test_network_is_optional_when_not_required() -> None:
    requirements = make_requirements().model_copy(
        update={"require_network_isolation": False}
    )
    guarantees = SandboxGuarantees(network=False)
    assert guarantees.supports(requirements) is True
def test_environment_filtering_is_optional_when_not_required() -> None:
    requirements = make_requirements().model_copy(
        update={"require_environment_filtering": False}
    )
    guarantees = SandboxGuarantees(environment=False)
    assert guarantees.supports(requirements) is True
class FakeSandbox:
    """Minimal test double implementing the sandbox protocol."""
    def __init__(self, guarantees: SandboxGuarantees) -> None:
        self.guarantees = guarantees
        self.released = False
    def establish(
        self,
        requirements: SandboxRequirements,
    ) -> SandboxGuarantees:
        return self.guarantees
    def require(
        self,
        requirements: SandboxRequirements,
    ) -> SandboxGuarantees:
        return self.guarantees
    def release(self) -> None:
        self.released = True
def test_require_sandbox_guarantees_accepts_valid_sandbox() -> None:
    requirements = make_requirements()
    sandbox = FakeSandbox(SandboxGuarantees())
    result = require_sandbox_guarantees(sandbox, requirements)
    assert result == SandboxGuarantees()
def test_require_sandbox_guarantees_blocks_unavailable_sandbox() -> None:
    requirements = make_requirements()
    sandbox = FakeSandbox(SandboxGuarantees(workspace=False))
    with pytest.raises(SandboxUnavailableError):
        require_sandbox_guarantees(sandbox, requirements)
def test_release_is_explicit_and_does_not_authorize_operations() -> None:
    sandbox = FakeSandbox(SandboxGuarantees())
    sandbox.release()
    assert sandbox.released is True
