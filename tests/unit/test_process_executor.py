"""Unit tests for bounded process executor (T042, T048)."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.execution.cancellation import CancellationToken
from coagent.execution.process import ProcessExecutor, sanitize_process_environment
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


def make_proc_def() -> ToolDefinition:
    return ToolDefinition(
        tool_id="process.execute",
        name="Process Execute",
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


def make_proc_req(workspace: Path, cmd: str, timeout: float = 10.0) -> ToolRequest:
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="process.execute",
        tool_version="1.0",
        arguments={"command": cmd, "timeout_seconds": timeout},
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(workspace),
        ),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=BASE_TIME,
    )


def test_sanitize_environment_strips_sensitive_keys() -> None:
    env = {
        "PATH": "C:/Windows",
        "AWS_SECRET_ACCESS_KEY": "AKIAIOSFODNN7EXAMPLE",
        "GITHUB_TOKEN": "ghp_1234567890abcdefghijklmnopqrst",
        "DB_PASSWORD": "supersecretpassword",
        "SAFE_PARAM": "hello",
    }
    sanitized = sanitize_process_environment(env)
    assert "PATH" in sanitized
    assert "SAFE_PARAM" in sanitized
    assert "AWS_SECRET_ACCESS_KEY" not in sanitized
    assert "GITHUB_TOKEN" not in sanitized
    assert "DB_PASSWORD" not in sanitized


def test_successful_command_execution(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = ProcessExecutor()

    # Run simple echo via python
    py = sys.executable
    cmd = f'"{py}" -c "print(\'hello from test\')"'
    req = make_proc_req(workspace, cmd)
    res = executor.execute(req, make_proc_def())

    assert res.status is ToolResultStatus.SUCCESS
    assert res.output is not None
    assert "hello from test" in res.output["stdout"]
    assert res.output["exit_code"] == 0


def test_process_timeout_enforced(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = ProcessExecutor()

    py = sys.executable
    cmd = f'"{py}" -c "import time; time.sleep(5)"'
    req = make_proc_req(workspace, cmd, timeout=0.3)
    res = executor.execute(req, make_proc_def())

    assert res.status is ToolResultStatus.FAILED
    assert res.error is not None
    assert res.error.code == "PROC_TIMEOUT"


def test_process_output_truncation_enforced(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    # Limit to 500 bytes max output
    executor = ProcessExecutor(max_output_bytes=500)

    py = sys.executable
    cmd = f'"{py}" -c "print(\'A\' * 2000)"'
    req = make_proc_req(workspace, cmd)
    res = executor.execute(req, make_proc_def())

    assert res.status is ToolResultStatus.SUCCESS
    assert res.output is not None
    assert res.output["truncated"] is True
    assert len(res.output["stdout"]) <= 600


def test_cancellation_terminates_running_process(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = ProcessExecutor()

    token = CancellationToken()
    token.cancel(reason="Execution cancelled by user.")

    py = sys.executable
    cmd = f'"{py}" -c "print(\'should not run\')"'
    req = make_proc_req(workspace, cmd)
    res = executor.execute(req, make_proc_def(), cancellation_token=token)

    assert res.status is ToolResultStatus.CANCELLED
