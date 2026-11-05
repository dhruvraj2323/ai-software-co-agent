"""Unit tests for scoped filesystem executor (T041)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.execution.cancellation import CancellationToken
from coagent.execution.filesystem import FilesystemExecutor
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ScopeEffect,
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


def make_def(tool_id: str, side_effect: ToolSideEffect) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name=tool_id,
        description="test",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[side_effect],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="fs",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


def make_req(workspace: Path, tool_id: str, arguments: dict[str, object]) -> ToolRequest:
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id=tool_id,
        tool_version="1.0",
        arguments=arguments,
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(workspace),
        ),
        autonomy_mode=AutonomyMode.ASSISTED_IMPLEMENT,
        source=ToolRequestSource.AGENT,
        created_at=BASE_TIME,
    )


def test_write_and_read_file_within_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = FilesystemExecutor()

    # Write file
    write_req = make_req(
        workspace,
        "workspace.write",
        {"path": "hello.txt", "content": "Hello World!"},
    )
    write_res = executor.execute(write_req, make_def("workspace.write", ToolSideEffect.WRITE))
    assert write_res.status is ToolResultStatus.SUCCESS
    assert write_res.scope_effect is ScopeEffect.MODIFIED
    assert (workspace / "hello.txt").read_text(encoding="utf-8") == "Hello World!"

    # Read file
    read_req = make_req(workspace, "workspace.read", {"path": "hello.txt"})
    read_res = executor.execute(read_req, make_def("workspace.read", ToolSideEffect.READ))
    assert read_res.status is ToolResultStatus.SUCCESS
    assert read_res.output is not None
    assert read_res.output["content"] == "Hello World!"


def test_out_of_workspace_write_fails_closed(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = FilesystemExecutor()

    req = make_req(
        workspace,
        "workspace.write",
        {"path": "../escape.txt", "content": "attack"},
    )
    res = executor.execute(req, make_def("workspace.write", ToolSideEffect.WRITE))
    assert res.status is ToolResultStatus.FAILED
    assert res.error is not None
    assert res.error.code == "FS_OUT_OF_SCOPE"
    assert not (tmp_path / "escape.txt").exists()


def test_modify_protected_path_fails_closed(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    git_dir = workspace / ".git"
    git_dir.mkdir()
    executor = FilesystemExecutor()

    req = make_req(
        workspace,
        "workspace.write",
        {"path": ".git/malicious.txt", "content": "forbidden"},
    )
    res = executor.execute(req, make_def("workspace.write", ToolSideEffect.WRITE))
    assert res.status is ToolResultStatus.FAILED
    assert res.error is not None
    assert res.error.code == "FS_PERMISSION_DENIED"


def test_list_and_delete_file(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "a.txt").write_text("a", encoding="utf-8")
    (workspace / "sub").mkdir()
    (workspace / "sub" / "b.txt").write_text("b", encoding="utf-8")

    executor = FilesystemExecutor()

    # List
    list_req = make_req(workspace, "workspace.list", {"path": "."})
    list_res = executor.execute(list_req, make_def("workspace.list", ToolSideEffect.READ))
    assert list_res.status is ToolResultStatus.SUCCESS
    assert list_res.output is not None
    entries = list_res.output["entries"]
    assert any(e["name"] == "a.txt" for e in entries)
    assert any(e["name"] == "sub" and e["is_directory"] for e in entries)

    # Delete
    del_req = make_req(workspace, "workspace.delete", {"path": "a.txt"})
    del_res = executor.execute(del_req, make_def("workspace.delete", ToolSideEffect.WRITE))
    assert del_res.status is ToolResultStatus.SUCCESS
    assert not (workspace / "a.txt").exists()


def test_cancellation_aborts_operation(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    executor = FilesystemExecutor()

    token = CancellationToken()
    token.cancel(reason="User interrupted.")

    req = make_req(workspace, "workspace.write", {"path": "abort.txt", "content": "data"})
    res = executor.execute(
        req,
        make_def("workspace.write", ToolSideEffect.WRITE),
        cancellation_token=token,
    )
    assert res.status is ToolResultStatus.CANCELLED
    assert not (workspace / "abort.txt").exists()
