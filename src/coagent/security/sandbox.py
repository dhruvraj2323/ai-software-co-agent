"""Pluggable sandbox interface and guarantee contracts."""
from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from coagent.security.limits import ResourceLimits
from coagent.workspace import WorkspaceScope


class SandboxGuarantee(StrEnum):
    """Security guarantees that a sandbox may provide."""
    WORKSPACE = "WORKSPACE"
    NETWORK = "NETWORK"
    ENVIRONMENT = "ENVIRONMENT"
    TIMEOUT = "TIMEOUT"
    OUTPUT = "OUTPUT"
    CONCURRENCY = "CONCURRENCY"
class SandboxUnavailableError(RuntimeError):
    """Raised when a required sandbox guarantee is unavailable."""
class SandboxRequirements(BaseModel):
    """Explicit guarantees required before controlled execution."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace: WorkspaceScope
    resource_limits: ResourceLimits
    require_network_isolation: bool = True
    require_environment_filtering: bool = True
class SandboxGuarantees(BaseModel):
    """Guarantees actually provided by an active sandbox."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace: bool = True
    network: bool = True
    environment: bool = True
    timeout: bool = True
    output: bool = True
    concurrency: bool = True
    def supports(self, requirement: SandboxRequirements) -> bool:
        """Return whether these guarantees satisfy the requirements."""
        if not self.workspace:
            return False
        if not self.timeout:
            return False
        if not self.output:
            return False
        if not self.concurrency:
            return False
        if requirement.require_network_isolation and not self.network:
            return False
        if (
            requirement.require_environment_filtering
            and not self.environment
        ):
            return False
        return True
class Sandbox(Protocol):
    """Internal pluggable sandbox boundary."""
    def establish(
        self,
        requirements: SandboxRequirements,
    ) -> SandboxGuarantees:
        """Establish a sandbox and return its effective guarantees."""
    def require(
        self,
        requirements: SandboxRequirements,
    ) -> SandboxGuarantees:
        """Require sandbox guarantees or fail closed."""
    def release(self) -> None:
        """Release the active sandbox resources."""
def require_sandbox_guarantees(
    sandbox: Sandbox,
    requirements: SandboxRequirements,
) -> SandboxGuarantees:
    """Require guarantees before execution can proceed."""
    guarantees = sandbox.require(requirements)
    if not guarantees.supports(requirements):
        raise SandboxUnavailableError(
            "required sandbox guarantees are unavailable"
        )
    return guarantees
def validate_sandbox_guarantees(
    guarantees: SandboxGuarantees,
    requirements: SandboxRequirements,
) -> None:
    """Fail closed when effective guarantees do not satisfy requirements."""
    if not guarantees.supports(requirements):
        raise SandboxUnavailableError(
            "required sandbox guarantees are unavailable"
        )
