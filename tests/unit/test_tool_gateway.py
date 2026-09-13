"""Unit tests for the canonical tool gateway."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ScopeEffect,
    ToolRequest,
    ToolRequestSource,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.gateway import ToolExecutor, ToolGateway
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRegistry,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)


def make_definition(
    *,
    tool_id: str = "workspace.read",
    version: str = "1.0",
    enabled: bool = True,
    executor: str = "workspace",
) -> ToolDefinition:
    """Create a valid tool definition for gateway tests."""
    return ToolDefinition(
        tool_id=tool_id,
        name="Workspace Read",
        description="Read files within the authorized workspace.",
        version=version,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
            },
        },
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default-read",
        executor=executor,
        origin=ToolOrigin.BUILTIN,
        enabled=enabled,
    )


def make_request(
    *,
    tool_id: str = "workspace.read",
    tool_version: str = "1.0",
) -> ToolRequest:
    """Create a valid tool request for gateway tests."""
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id=tool_id,
        tool_version=tool_version,
        arguments={"path": "README.md"},
        requested_scope=Scope(
            workspace_id=uuid4(),
            root="C:/Projects/ai-software-co-agent",
        ),
        autonomy_mode=AutonomyMode.CHAT,
        source=ToolRequestSource.USER,
        created_at=datetime.now(UTC),
    )


def make_result(request: ToolRequest) -> ToolResult:
    """Create a successful result for a gateway test executor."""
    return ToolResult(
        request_id=request.request_id,
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"content": "hello"},
        scope_effect=ScopeEffect.UNCHANGED,
        created_at=datetime.now(UTC),
    )


class RecordingExecutor:
    """Test executor that records every routed request."""

    def __init__(self) -> None:
        self.requests: list[tuple[ToolRequest, ToolDefinition]] = []

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> ToolResult:
        self.requests.append((request, definition))
        return make_result(request)


def test_registered_tool_call_routes_through_gateway() -> None:
    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition)
    executor = RecordingExecutor()
    resolved: list[ToolDefinition] = []

    def resolve(candidate: ToolDefinition) -> ToolExecutor:
        resolved.append(candidate)
        return executor

    gateway = ToolGateway(registry, resolve)
    request = make_request()
    result = gateway.route(request)
    assert result.request_id == request.request_id
    assert result.success is True
    assert executor.requests == [(request, definition)]
    assert resolved == [definition]


def test_gateway_uses_registered_definition_for_executor_resolution() -> None:
    registry = ToolRegistry()
    definition = make_definition(executor="workspace-reader")
    registry.register(definition)
    executor = RecordingExecutor()
    resolved: list[str] = []

    def resolve(candidate: ToolDefinition) -> ToolExecutor:
        resolved.append(candidate.executor)
        return executor

    gateway = ToolGateway(registry, resolve)
    gateway.route(make_request())
    assert resolved == ["workspace-reader"]


def test_gateway_rejects_unknown_tool() -> None:
    registry = ToolRegistry()
    executor = RecordingExecutor()
    gateway = ToolGateway(
        registry,
        lambda _: executor,
    )
    with pytest.raises(
        KeyError,
        match="unknown tool: workspace.read",
    ):
        gateway.route(make_request())


def test_gateway_rejects_disabled_tool() -> None:
    registry = ToolRegistry()
    registry.register(make_definition(enabled=False))
    executor = RecordingExecutor()
    gateway = ToolGateway(
        registry,
        lambda _: executor,
    )
    with pytest.raises(
        ValueError,
        match="tool is disabled: workspace.read",
    ):
        gateway.route(make_request())
    assert executor.requests == []


def test_gateway_rejects_version_mismatch() -> None:
    registry = ToolRegistry()
    registry.register(make_definition(version="2.0"))
    executor = RecordingExecutor()
    gateway = ToolGateway(
        registry,
        lambda _: executor,
    )
    with pytest.raises(
        ValueError,
        match=(
            r"tool version mismatch: workspace\.read "
            r"requested=1\.0 registered=2\.0"
        ),
    ):
        gateway.route(make_request(tool_version="1.0"))
    assert executor.requests == []


def test_gateway_does_not_execute_without_registry_registration() -> None:
    registry = ToolRegistry()
    executor = RecordingExecutor()
    resolver_called = False

    def resolve(_: ToolDefinition) -> ToolExecutor:
        nonlocal resolver_called
        resolver_called = True
        return executor

    gateway = ToolGateway(registry, resolve)
    with pytest.raises(KeyError):
        gateway.route(make_request())
    assert resolver_called is False
    assert executor.requests == []


def test_gateway_preserves_tool_result_from_executor() -> None:
    registry = ToolRegistry()
    registry.register(make_definition())
    executor = RecordingExecutor()
    gateway = ToolGateway(
        registry,
        lambda _: executor,
    )
    request = make_request()
    expected = make_result(request)

    class FixedExecutor:
        def execute(
            self,
            received_request: ToolRequest,
            definition: ToolDefinition,
        ) -> ToolResult:
            assert definition.tool_id == "workspace.read"
            assert received_request is request
            return expected

    gateway = ToolGateway(
        registry,
        lambda _: FixedExecutor(),
    )
    result = gateway.route(request)
    assert result is expected


def test_gateway_does_not_create_authorization_decisions() -> None:
    registry = ToolRegistry()
    registry.register(make_definition())
    executor = RecordingExecutor()
    gateway = ToolGateway(
        registry,
        lambda _: executor,
    )
    result = gateway.route(make_request())
    assert result.status is ToolResultStatus.SUCCESS
    assert not hasattr(gateway, "policy")
    assert not hasattr(gateway, "approval")


def test_gateway_result_error_contract_remains_executor_owned() -> None:
    registry = ToolRegistry()
    registry.register(make_definition())
    request = make_request()
    error = ErrorRecord(
        error_id=uuid4(),
        task_id=request.task_id,
        correlation_id=request.correlation_id,
        category="TOOL",
        code="TOOL_EXECUTION_FAILED",
        source="test-executor",
        message="execution failed",
        severity=EventSeverity.ERROR,
        recoverability=Recoverability.MANUAL,
        occurred_at=datetime.now(UTC),
        normalized_at=datetime.now(UTC),
    )

    class ErrorExecutor:
        def execute(
            self,
            received_request: ToolRequest,
            definition: ToolDefinition,
        ) -> ToolResult:
            return ToolResult(
                request_id=received_request.request_id,
                success=False,
                status=ToolResultStatus.FAILED,
                error=error,
                scope_effect=ScopeEffect.NONE,
                created_at=datetime.now(UTC),
            )

    gateway = ToolGateway(
        registry,
        lambda _: ErrorExecutor(),
    )
    result = gateway.route(request)
    assert result.success is False
    assert result.status is ToolResultStatus.FAILED
    assert result.error == error
