"""T038 security regression tests for tool/policy authorization bypasses."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.policy import PolicyDecisionOutcome, PolicyEvaluator, PolicyRequest
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

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


class RecordingExecutor:
    """Executor that records calls so tests can detect unauthorized execution."""

    def __init__(self) -> None:
        self.calls: list[ToolRequest] = []

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> ToolResult:
        self.calls.append(request)
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={"executed": True},
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=BASE_TIME,
        )


def make_definition(
    *,
    tool_id: str = "workspace.read",
    version: str = "1.0",
    enabled: bool = True,
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW,
    side_effects: list[ToolSideEffect] | None = None,
    capability: ToolCapability = ToolCapability.WORKSPACE_READ,
    resource_scope: ToolScope = ToolScope.WORKSPACE,
) -> ToolDefinition:
    """Build a registered tool definition for adversarial tests."""
    return ToolDefinition(
        tool_id=tool_id,
        name="Test Workspace Tool",
        description="A tool used to test authorization boundaries.",
        version=version,
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
        },
        output_schema={"type": "object"},
        capability=capability,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="test-executor",
        origin=ToolOrigin.BUILTIN,
        enabled=enabled,
    )


def make_request(
    root: Path,
    *,
    path: str | None = None,
    tool_id: str = "workspace.read",
    version: str = "1.0",
    autonomy_mode: AutonomyMode = AutonomyMode.ASSISTED_IMPLEMENT,
    source: ToolRequestSource = ToolRequestSource.AGENT,
) -> ToolRequest:
    """Build a canonical tool request with controllable authorization inputs."""
    arguments: dict[str, object] = {}
    if path is not None:
        arguments["path"] = path

    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id=tool_id,
        tool_version=version,
        arguments=arguments,
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(root),
        ),
        autonomy_mode=autonomy_mode,
        source=source,
        created_at=BASE_TIME,
    )


def make_policy_request(request: ToolRequest) -> PolicyRequest:
    """Convert a tool request to the corresponding policy input."""
    return PolicyRequest(
        request_id=request.request_id,
        task_id=request.task_id,
        correlation_id=request.correlation_id,
        tool_id=request.tool_id,
        tool_version=request.tool_version,
        arguments=request.arguments,
        requested_scope=request.requested_scope,
        autonomy_mode=request.autonomy_mode,
        source=request.source,
        risk_level=ToolRiskLevel.LOW,
        created_at=request.created_at,
    )


@pytest.mark.parametrize("source", list(ToolRequestSource))
@pytest.mark.parametrize("mode", list(AutonomyMode))
def test_out_of_workspace_target_remains_denied(
    tmp_path: Path,
    source: ToolRequestSource,
    mode: AutonomyMode,
) -> None:
    """Changing caller origin or autonomy must not authorize a workspace escape."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside workspace", encoding="utf-8")

    request = make_request(
        workspace,
        path=str(outside),
        source=source,
        autonomy_mode=mode,
    )
    definition = make_definition()

    decision = PolicyEvaluator().evaluate(
        make_policy_request(request),
        definition,
        now=BASE_TIME,
    )

    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.scope.out_of_scope"


@pytest.mark.parametrize("source", list(ToolRequestSource))
@pytest.mark.parametrize("mode", list(AutonomyMode))
def test_protected_git_path_remains_denied(
    tmp_path: Path,
    source: ToolRequestSource,
    mode: AutonomyMode,
) -> None:
    """Changing caller origin or autonomy must not authorize protected VCS paths."""
    workspace = tmp_path / "workspace"
    git_directory = workspace / ".git"
    git_directory.mkdir(parents=True)

    request = make_request(
        workspace,
        path=".git",
        source=source,
        autonomy_mode=mode,
    )

    decision = PolicyEvaluator().evaluate(
        make_policy_request(request),
        make_definition(),
        now=BASE_TIME,
    )

    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.resource.protected"


def test_tool_identity_mismatch_cannot_be_authorized(
    tmp_path: Path,
) -> None:
    """A request for one tool cannot borrow another tool's definition."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    request = make_request(workspace, tool_id="terminal.powershell")
    definition = make_definition(tool_id="workspace.read")

    decision = PolicyEvaluator().evaluate(
        make_policy_request(request),
        definition,
        now=BASE_TIME,
    )

    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.tool.identity.mismatch"


def test_gateway_does_not_execute_out_of_scope_request(
    tmp_path: Path,
) -> None:
    """A policy-denied path must not execute through an alternate gateway path."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("must not be accessed", encoding="utf-8")

    definition = make_definition()
    registry = ToolRegistry()
    registry.register(definition)

    executor = RecordingExecutor()

    def resolve_executor(_: ToolDefinition) -> ToolExecutor:
        return executor

    gateway = ToolGateway(registry, resolve_executor)
    request = make_request(workspace, path=str(outside))

    # Establish the expected hard denial before testing execution.
    decision = PolicyEvaluator().evaluate(
        make_policy_request(request),
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY

    # Security invariant: a denied request must never reach an executor.
    # This currently exposes the gateway's missing policy-enforcement seam.
    try:
        gateway.route(request)
    except KeyError, ValueError:
        pass

    assert executor.calls == [], (
        "Security bypass: ToolGateway executed a request that policy DENIED."
    )
