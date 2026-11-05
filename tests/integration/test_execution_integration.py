"""Integration tests connecting Tool Gateway to execution engines (T047)."""

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
from coagent.tools.gateway import ToolGateway
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRegistry,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def make_workspace_req(
    workspace: Path,
    tool_id: str,
    args: dict[str, object],
    mode: AutonomyMode = AutonomyMode.ASSISTED_IMPLEMENT,
) -> ToolRequest:
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
        autonomy_mode=mode,
        source=ToolRequestSource.AGENT,
        created_at=BASE_TIME,
    )


def test_gateway_routes_to_filesystem_executor(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "data.txt").write_text("hello from disk", encoding="utf-8")

    registry = ToolRegistry()
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
    registry.register(fs_def)

    fs_executor = FilesystemExecutor()
    gateway = ToolGateway(
        registry,
        lambda d: fs_executor,
    )

    req = make_workspace_req(workspace, "workspace.read", {"path": "data.txt"})
    result = gateway.route(req)

    assert result.status is ToolResultStatus.SUCCESS
    assert result.output is not None
    assert result.output["content"] == "hello from disk"


def test_gateway_routes_to_process_executor(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    registry = ToolRegistry()
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
    registry.register(proc_def)

    proc_executor = ProcessExecutor()
    gateway = ToolGateway(
        registry,
        lambda d: proc_executor,
    )

    py = sys.executable
    req = make_workspace_req(
        workspace,
        "process.execute",
        {"command": f'"{py}" -c "print(\'gateway ok\')"', "cwd": "."},
        mode=AutonomyMode.SUPERVISED_AUTO,
    )
    result = gateway.route(req)

    assert result.status is ToolResultStatus.SUCCESS
    assert result.output is not None
    assert "gateway ok" in result.output["stdout"]
