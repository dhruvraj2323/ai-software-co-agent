"""Unit tests for T036 policy scope and risk evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.policy import (
    PolicyDecisionOutcome,
    PolicyEvaluator,
    PolicyRequest,
)
from coagent.security import ProtectedPathPolicy
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequestSource,
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


def make_request(
    *,
    arguments: dict[str, object] | None = None,
    autonomy_mode: AutonomyMode = AutonomyMode.ASSISTED_IMPLEMENT,
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW,
) -> PolicyRequest:
    return PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.read",
        tool_version="1.0",
        arguments=arguments if arguments is not None else {"path": "src"},
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=".",
        ),
        autonomy_mode=autonomy_mode,
        source=ToolRequestSource.AGENT,
        risk_level=risk_level,
        created_at=BASE_TIME,
    )


def make_definition(
    *,
    tool_id: str = "workspace.read",
    version: str = "1.0",
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW,
    side_effects: list[ToolSideEffect] | None = None,
    resource_scope: ToolScope = ToolScope.WORKSPACE,
    enabled: bool = True,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name="Workspace Read",
        description="Read workspace content.",
        version=version,
        input_schema={},
        output_schema={},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="workspace.read",
        origin=ToolOrigin.BUILTIN,
        enabled=enabled,
    )


def make_workspace(tmp_path: Path) -> tuple[Path, Scope]:
    root = tmp_path / "workspace"
    root.mkdir()
    return root, Scope(
        workspace_id=uuid4(),
        root=str(root),
    )


def test_low_risk_in_scope_read_is_allowed(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    request = make_request()
    request.requested_scope = scope
    definition = make_definition()
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.ALLOW
    assert decision.rule_id == "policy.allow.scoped"
    assert decision.evaluated_scope == scope


def test_out_of_scope_target_is_denied(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    request = make_request(arguments={"path": str(outside)})
    request.requested_scope = scope
    definition = make_definition()
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.scope.out_of_scope"


def test_protected_target_is_denied(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / ".git").mkdir()
    request = make_request(arguments={"path": ".git"})
    request.requested_scope = scope
    definition = make_definition()
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.resource.protected"


def test_missing_scoped_target_requires_approval(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request(arguments={})
    request.requested_scope = scope
    definition = make_definition()
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.scope.ambiguous"


def test_high_risk_operation_requires_approval(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    request = make_request(
        arguments={"path": "src"},
        risk_level=ToolRiskLevel.HIGH,
    )
    request.requested_scope = scope
    definition = make_definition(
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.risk.high"


def test_destructive_operation_requires_approval(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    request = make_request(arguments={"path": "src"})
    request.requested_scope = scope
    definition = make_definition(
        risk_level=ToolRiskLevel.MEDIUM,
        side_effects=[ToolSideEffect.DESTRUCTIVE],
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.risk.high"


def test_medium_write_operation_is_restricted(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    request = make_request(
        arguments={"path": "src"},
        risk_level=ToolRiskLevel.MEDIUM,
    )
    request.requested_scope = scope
    definition = make_definition(
        risk_level=ToolRiskLevel.MEDIUM,
        side_effects=[ToolSideEffect.WRITE],
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.RESTRICT
    assert decision.rule_id == "policy.risk.medium"


def test_external_resource_requires_approval(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request(arguments={"target": "external-resource"})
    request.requested_scope = scope
    definition = make_definition(
        risk_level=ToolRiskLevel.VARIABLE,
        side_effects=[ToolSideEffect.EXTERNAL],
        resource_scope=ToolScope.EXTERNAL,
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.resource.external"


def test_restricted_mode_denies_non_low_risk(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    request = make_request(
        arguments={"path": "src"},
        autonomy_mode=AutonomyMode.RESTRICTED,
        risk_level=ToolRiskLevel.MEDIUM,
    )
    request.requested_scope = scope
    definition = make_definition(
        risk_level=ToolRiskLevel.MEDIUM,
        side_effects=[ToolSideEffect.WRITE],
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.autonomy.restricted"


def test_tool_version_mismatch_is_denied(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request()
    request.requested_scope = scope
    definition = make_definition(version="2.0")
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.tool.version.mismatch"


def test_disabled_tool_is_denied(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request()
    request.requested_scope = scope
    definition = make_definition(enabled=False)
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.tool.disabled"


def test_tool_identity_mismatch_is_denied(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request()
    request.requested_scope = scope
    definition = make_definition(tool_id="search.text")
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.tool.identity.mismatch"


def test_policy_decision_preserves_request_correlation(tmp_path: Path) -> None:
    _, scope = make_workspace(tmp_path)
    request = make_request()
    request.requested_scope = scope
    definition = make_definition()
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.request_id == request.request_id
    assert decision.task_id == request.task_id
    assert decision.correlation_id == request.correlation_id
    assert decision.created_at == BASE_TIME


@pytest.mark.parametrize(
    "side_effect",
    [
        ToolSideEffect.READ,
        ToolSideEffect.WRITE,
        ToolSideEffect.EXECUTE,
    ],
)
def test_side_effects_influence_decision(
    tmp_path: Path,
    side_effect: ToolSideEffect,
) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "src").mkdir()
    risk = ToolRiskLevel.LOW if side_effect is ToolSideEffect.READ else ToolRiskLevel.MEDIUM
    request = make_request(
        arguments={"path": "src"},
        risk_level=risk,
    )
    request.requested_scope = scope
    definition = make_definition(
        risk_level=risk,
        side_effects=[side_effect],
    )
    decision = PolicyEvaluator().evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    expected = (
        PolicyDecisionOutcome.ALLOW
        if side_effect is ToolSideEffect.READ
        else PolicyDecisionOutcome.RESTRICT
    )
    assert decision.outcome is expected


def test_protected_path_policy_can_be_injected(tmp_path: Path) -> None:
    root, scope = make_workspace(tmp_path)
    (root / "internal").mkdir()
    policy = ProtectedPathPolicy(("internal",))
    evaluator = PolicyEvaluator(policy)
    request = make_request(arguments={"path": "internal"})
    request.requested_scope = scope
    definition = make_definition()
    decision = evaluator.evaluate(
        request,
        definition,
        now=BASE_TIME,
    )
    assert decision.outcome is PolicyDecisionOutcome.DENY
