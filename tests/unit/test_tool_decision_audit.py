"""T039 unit tests for material tool decision audit hooks."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.audit.hooks import InMemoryAuditHook
from coagent.policy.contracts import PolicyDecisionOutcome
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ScopeEffect,
    ToolRequest,
    ToolRequestSource,
    ToolResult,
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


class SimpleExecutor:
    """Mock executor for audit hook tests."""

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> ToolResult:
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
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW,
    side_effects: list[ToolSideEffect] | None = None,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name="Audit Test Tool",
        description="Tool used to verify audit hooks.",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="test-executor",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


def make_request(
    root: Path,
    *,
    path: str = "src",
    tool_id: str = "workspace.read",
    autonomy_mode: AutonomyMode = AutonomyMode.ASSISTED_IMPLEMENT,
) -> ToolRequest:
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id=tool_id,
        tool_version="1.0",
        arguments={"path": path},
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(root),
        ),
        autonomy_mode=autonomy_mode,
        source=ToolRequestSource.AGENT,
        created_at=BASE_TIME,
    )


def test_allowed_decision_is_recorded_by_audit_hook(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src").mkdir(parents=True)

    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition)

    audit_hook = InMemoryAuditHook()
    gateway = ToolGateway(
        registry,
        lambda _: SimpleExecutor(),
        audit_hook=audit_hook,
    )

    request = make_request(workspace)
    result = gateway.route(request)

    assert result.status is ToolResultStatus.SUCCESS
    assert len(audit_hook.records) == 1

    decision, recorded_req, recorded_def = audit_hook.records[0]
    assert decision.outcome is PolicyDecisionOutcome.ALLOW
    assert decision.request_id == request.request_id
    assert recorded_req.request_id == request.request_id
    assert recorded_def.tool_id == definition.tool_id


def test_denied_decision_is_traceable_in_audit_hook(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")

    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition)

    audit_hook = InMemoryAuditHook()
    gateway = ToolGateway(
        registry,
        lambda _: SimpleExecutor(),
        audit_hook=audit_hook,
    )

    request = make_request(workspace, path=str(outside))
    with pytest.raises(ValueError, match="denied by policy"):
        gateway.route(request)

    assert len(audit_hook.records) == 1
    decision, recorded_req, _ = audit_hook.records[0]
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.scope.out_of_scope"
    assert decision.request_id == request.request_id


def test_approval_required_decision_is_traceable(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src").mkdir(parents=True)

    registry = ToolRegistry()
    definition = make_definition(
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
    )
    registry.register(definition)

    audit_hook = InMemoryAuditHook()
    gateway = ToolGateway(
        registry,
        lambda _: SimpleExecutor(),
        audit_hook=audit_hook,
    )

    request = make_request(workspace)
    with pytest.raises(ValueError, match="requires approval"):
        gateway.route(request)

    assert len(audit_hook.records) == 1
    decision, recorded_req, _ = audit_hook.records[0]
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.risk.high"
    assert decision.request_id == request.request_id
