"""Security and resource bounding tests for execution subsystem (T047, T048)."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.execution.filesystem import FilesystemExecutor
from coagent.execution.process import ProcessExecutor
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

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def make_exec_req(workspace: Path, tool_id: str, args: dict[str, object]) -> ToolRequest:
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id=tool_id,
        tool_version="1.0",
        arguments=args,
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(workspace),
        ),
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        created_at=BASE_TIME,
    )


def test_filesystem_executor_blocks_dotdot_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    secret = tmp_path / "outside.txt"
    secret.write_text("private", encoding="utf-8")

    executor = FilesystemExecutor()
    req = make_exec_req(workspace, "workspace.read", {"path": "../outside.txt"})
    fs_def = ToolDefinition(
        tool_id="workspace.read",
        name="Read File",
        description="Reads a file in workspace",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="filesystem",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )
    result = executor.execute(req, fs_def)
    assert result.status is ToolResultStatus.FAILED
    assert result.error is not None
    assert result.error.code == "FS_OUT_OF_SCOPE"


def test_process_executor_blocks_outside_cwd(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()

    executor = ProcessExecutor()
    proc_def = ToolDefinition(
        tool_id="process.execute",
        name="Run Process",
        description="Run bounded command",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.MEDIUM,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="process",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )
    req = make_exec_req(
        workspace,
        "process.execute",
        {"command": "echo test", "cwd": "../outside"},
    )
    result = executor.execute(req, proc_def)
    assert result.status is ToolResultStatus.FAILED
    assert result.error is not None
    assert result.error.code == "PROC_OUT_OF_SCOPE"


def test_process_executor_bounds_huge_output(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Max output limited to 1024 bytes
    executor = ProcessExecutor(max_output_bytes=1024)
    proc_def = ToolDefinition(
        tool_id="process.execute",
        name="Run Process",
        description="Run bounded command",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.MEDIUM,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="process",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )

    py = sys.executable
    req = make_exec_req(
        workspace,
        "process.execute",
        {"command": f'"{py}" -c "print(\'X\' * 50000)"'},
    )
    result = executor.execute(req, proc_def)
    assert result.status is ToolResultStatus.SUCCESS
    assert result.output is not None
    assert result.output["truncated"] is True
    assert len(result.output["stdout"]) <= 1200
