"""Shared security-boundary adversarial fixtures."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.security import ResourceLimits, SandboxRequirements
from coagent.workspace import WorkspaceScope


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """Create an isolated workspace root."""
    root = tmp_path / "workspace"
    root.mkdir()
    return root
@pytest.fixture
def outside_root(tmp_path: Path) -> Path:
    """Create a sibling directory outside the workspace."""
    root = tmp_path / "outside"
    root.mkdir()
    return root
@pytest.fixture
def workspace_scope(workspace_root: Path) -> WorkspaceScope:
    """Create an explicit task-owned workspace scope."""
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_root),
    )
@pytest.fixture
def resource_limits() -> ResourceLimits:
    """Create small deterministic resource limits."""
    return ResourceLimits(
        max_execution_seconds=1.0,
        max_concurrent_operations=1,
        max_tool_calls=1,
        max_recovery_attempts=1,
        max_output_bytes=8,
    )
@pytest.fixture
def sandbox_requirements(
    workspace_scope: WorkspaceScope,
    resource_limits: ResourceLimits,
) -> SandboxRequirements:
    """Create explicit sandbox requirements."""
    return SandboxRequirements(
        workspace=workspace_scope,
        resource_limits=resource_limits,
    )
