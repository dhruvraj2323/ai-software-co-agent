"""Workspace and Process Escape Attack Validation Suite.

Verifies ST-SBX-001, ST-SBX-002, ST-SBX-003, ST-EXE-001, ST-EXE-002 according to:
- docs/specifications/10 AI_Software_CoAgent_Security_Sandbox_Specification_v1.0_FINAL_LOCKED.md
- docs/specifications/09 AI_Software_CoAgent_Testing_Validation_Specification_v1.0_FINAL_LOCKED.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.execution.filesystem import FilesystemExecutor
from coagent.execution.process import ProcessExecutor
from coagent.policy.evaluator import (
    PolicyDecisionOutcome,
    PolicyEvaluator,
    PolicyRequest,
)
from coagent.security.path import WorkspaceEscapeError, require_path_within_workspace
from coagent.security.policy import is_protected_path
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequest,
    ToolRequestSource,
    ToolResultStatus,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.workspace.scope import WorkspaceScope
from tests.fixtures.repo_fixtures import create_protected_paths_repo


def make_tool_def(
    tool_id: str,
    capability: ToolCapability,
    risk_level: ToolRiskLevel = ToolRiskLevel.HIGH,
    side_effects: list[ToolSideEffect] | None = None,
    resource_scope: ToolScope = ToolScope.WORKSPACE,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name=tool_id,
        description=f"Test capability for {tool_id}",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=capability,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="test",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


@pytest.fixture
def protected_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "protected_repo"
    create_protected_paths_repo(ws)
    return ws


@pytest.fixture
def scope(protected_workspace: Path) -> WorkspaceScope:
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(protected_workspace),
    )


# ST-SBX-001: Path traversal attacks are strictly blocked
@pytest.mark.parametrize(
    "attack_path",
    [
        "../../outside.txt",
        "sub/dir/../../../../escape.json",
        "..\\..\\windows_traversal.txt",
        "nested/../../../../../../../../Windows/System32/calc.exe",
        "C:/Windows/win.ini",
        "/etc/passwd",
    ],
)
def test_st_sbx_001_path_traversal_attacks(scope: WorkspaceScope, attack_path: str) -> None:
    with pytest.raises(WorkspaceEscapeError):
        require_path_within_workspace(scope, attack_path)


# ST-SBX-002: Symlink escape attacks are strictly blocked
def test_st_sbx_002_symlink_escape(scope: WorkspaceScope, tmp_path: Path) -> None:
    outside_target = tmp_path / "outside_target.txt"
    outside_target.write_text("sensitive outside data", encoding="utf-8")

    ws_path = Path(scope.root)
    symlink_path = ws_path / "evil_symlink.txt"

    try:
        symlink_path.symlink_to(outside_target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation requires elevated permissions on this Windows host")

    with pytest.raises(WorkspaceEscapeError):
        require_path_within_workspace(scope, "evil_symlink.txt")


# ST-SBX-003: Protected paths cannot be modified or deleted
@pytest.mark.parametrize(
    "protected_relative_path",
    [
        ".git/HEAD",
        ".git/config",
        ".env",
        "credentials.pem",
    ],
)
def test_st_sbx_003_protected_paths(scope: WorkspaceScope, protected_relative_path: str) -> None:
    assert is_protected_path(scope, protected_relative_path)

    # Filesystem executor must reject writes/deletions on protected paths
    fs = FilesystemExecutor()
    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.write",
        tool_version="1.0",
        arguments={"path": protected_relative_path, "content": "tampered"},
        requested_scope=Scope(workspace_id=uuid4(), root=str(scope.root)),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    res = fs.execute(
        req,
        make_tool_def(
            "workspace.write",
            ToolCapability.WORKSPACE_WRITE,
            side_effects=[ToolSideEffect.WRITE],
        ),
    )
    assert not res.success
    assert res.status == ToolResultStatus.FAILED


# ST-EXE-001: Shell chaining cannot bypass policy
def test_st_exe_001_shell_chaining() -> None:
    evaluator = PolicyEvaluator()
    tool_def = make_tool_def(
        tool_id="process.exec",
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.PROCESS,
    )

    policy_req = PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="process.exec",
        tool_version="1.0",
        arguments={"command": "dir && format C:"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/workspace"),
        autonomy_mode=AutonomyMode.RESTRICTED,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.HIGH,
        created_at=datetime.now(UTC),
    )
    decision = evaluator.evaluate(policy_req, tool_def)
    # Shell chaining command cannot gain automatic ALLOW in RESTRICTED mode
    assert decision.outcome != PolicyDecisionOutcome.ALLOW


# ST-EXE-002: Alternate interpreter invocation cannot bypass policy
def test_st_exe_002_interpreter_switch() -> None:
    evaluator = PolicyEvaluator()
    tool_def = make_tool_def(
        tool_id="process.exec",
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.PROCESS,
    )

    policy_req = PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="process.exec",
        tool_version="1.0",
        arguments={"command": "powershell.exe -ExecutionPolicy Bypass -Command 'Get-Process'"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/workspace"),
        autonomy_mode=AutonomyMode.RESTRICTED,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.HIGH,
        created_at=datetime.now(UTC),
    )
    decision = evaluator.evaluate(policy_req, tool_def)
    assert decision.outcome != PolicyDecisionOutcome.ALLOW


# Process execution timeout bounds
def test_process_execution_timeout(tmp_path: Path) -> None:
    # Process executor must terminate when timeout is exceeded
    executor = ProcessExecutor(default_timeout_seconds=0.5)
    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="process.exec",
        tool_version="1.0",
        # Use python to sleep longer than timeout
        arguments={"command": "python -c \"import time; time.sleep(5)\""},
        requested_scope=Scope(workspace_id=uuid4(), root=str(tmp_path)),
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    tool_def = make_tool_def(
        tool_id="process.exec",
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.PROCESS,
    )
    res = executor.execute(req, tool_def)
    assert not res.success
    assert res.status in (ToolResultStatus.FAILED, ToolResultStatus.BLOCKED)
    err_msg = res.error.message if hasattr(res.error, "message") else str(res.error)
    assert "timed out" in err_msg.lower() or "timeout" in err_msg.lower()
