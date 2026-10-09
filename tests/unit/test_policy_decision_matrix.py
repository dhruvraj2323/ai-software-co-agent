"""T037 policy decision matrix tests.
These tests verify expected policy outcomes without changing production code.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.policy import PolicyDecisionOutcome, PolicyEvaluator, PolicyRequest
from coagent.tools.contracts import AutonomyMode, Scope, ToolRequestSource
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
    root: Path,
    autonomy_mode: AutonomyMode,
    risk_level: ToolRiskLevel,
    arguments: dict[str, object],
) -> PolicyRequest:
    """Build a canonical policy request for a matrix case."""
    return PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.read",
        tool_version="1.0",
        arguments=arguments,
        requested_scope=Scope(
            workspace_id=uuid4(),
            root=str(root),
        ),
        autonomy_mode=autonomy_mode,
        source=ToolRequestSource.AGENT,
        risk_level=risk_level,
        created_at=BASE_TIME,
    )


def make_definition(
    *,
    risk_level: ToolRiskLevel,
    side_effect: ToolSideEffect,
    resource_scope: ToolScope,
) -> ToolDefinition:
    """Build registered tool metadata for a matrix case."""
    return ToolDefinition(
        tool_id="workspace.read",
        name="Policy Matrix Tool",
        description="Tool definition used by T037 policy matrix tests.",
        version="1.0",
        input_schema={},
        output_schema={},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=risk_level,
        side_effects=[side_effect],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="workspace.read",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


@pytest.mark.parametrize(
    "autonomy_mode",
    list(AutonomyMode),
    ids=lambda mode: mode.value,
)
def test_low_risk_read_is_allowed_across_autonomy_modes(
    tmp_path: Path,
    autonomy_mode: AutonomyMode,
) -> None:
    """A low-risk, in-scope read remains read-only in every mode."""
    root = tmp_path / "workspace"
    (root / "src").mkdir(parents=True)
    request = make_request(
        root=root,
        autonomy_mode=autonomy_mode,
        risk_level=ToolRiskLevel.LOW,
        arguments={"path": "src"},
    )
    definition = make_definition(
        risk_level=ToolRiskLevel.LOW,
        side_effect=ToolSideEffect.READ,
        resource_scope=ToolScope.WORKSPACE,
    )
    decision = PolicyEvaluator().evaluate(request, definition, now=BASE_TIME)
    assert decision.outcome is PolicyDecisionOutcome.ALLOW
    assert decision.request_id == request.request_id
    assert decision.task_id == request.task_id
    assert decision.correlation_id == request.correlation_id


@pytest.mark.parametrize(
    ("autonomy_mode", "expected"),
    [
        (AutonomyMode.CHAT, PolicyDecisionOutcome.DENY),
        (AutonomyMode.PLAN, PolicyDecisionOutcome.DENY),
        (
            AutonomyMode.ASSISTED_IMPLEMENT,
            PolicyDecisionOutcome.RESTRICT,
        ),
        (AutonomyMode.SUPERVISED_AUTO, PolicyDecisionOutcome.RESTRICT),
        (AutonomyMode.AUTONOMOUS, PolicyDecisionOutcome.RESTRICT),
        (AutonomyMode.RESTRICTED, PolicyDecisionOutcome.DENY),
    ],
    ids=lambda value: value.value if isinstance(value, StrEnum) else str(value),
)
@pytest.mark.parametrize(
    "side_effect",
    [ToolSideEffect.WRITE, ToolSideEffect.EXECUTE],
    ids=lambda effect: effect.value,
)
def test_medium_side_effect_decision_matrix(
    tmp_path: Path,
    autonomy_mode: AutonomyMode,
    expected: PolicyDecisionOutcome,
    side_effect: ToolSideEffect,
) -> None:
    """Mutation/execution must follow the selected autonomy posture."""
    root = tmp_path / "workspace"
    (root / "src").mkdir(parents=True)
    request = make_request(
        root=root,
        autonomy_mode=autonomy_mode,
        risk_level=ToolRiskLevel.MEDIUM,
        arguments={"path": "src"},
    )
    definition = make_definition(
        risk_level=ToolRiskLevel.MEDIUM,
        side_effect=side_effect,
        resource_scope=ToolScope.WORKSPACE,
    )
    decision = PolicyEvaluator().evaluate(request, definition, now=BASE_TIME)
    assert decision.outcome is expected


@pytest.mark.parametrize(
    "autonomy_mode",
    list(AutonomyMode),
    ids=lambda mode: mode.value,
)
def test_high_risk_operation_requires_approval_across_modes(
    tmp_path: Path,
    autonomy_mode: AutonomyMode,
) -> None:
    """High-risk actions require approval; autonomy cannot bypass that rule."""
    root = tmp_path / "workspace"
    (root / "src").mkdir(parents=True)
    request = make_request(
        root=root,
        autonomy_mode=autonomy_mode,
        risk_level=ToolRiskLevel.HIGH,
        arguments={"path": "src"},
    )
    definition = make_definition(
        risk_level=ToolRiskLevel.HIGH,
        side_effect=ToolSideEffect.EXECUTE,
        resource_scope=ToolScope.WORKSPACE,
    )
    decision = PolicyEvaluator().evaluate(request, definition, now=BASE_TIME)
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.risk.high"


@pytest.mark.parametrize(
    "autonomy_mode",
    list(AutonomyMode),
    ids=lambda mode: mode.value,
)
def test_external_resource_requires_approval_in_every_mode(
    tmp_path: Path,
    autonomy_mode: AutonomyMode,
) -> None:
    """Autonomy mode cannot silently authorize external resources."""
    root = tmp_path / "workspace"
    root.mkdir()
    request = make_request(
        root=root,
        autonomy_mode=autonomy_mode,
        risk_level=ToolRiskLevel.VARIABLE,
        arguments={"target": "external-resource"},
    )
    definition = make_definition(
        risk_level=ToolRiskLevel.VARIABLE,
        side_effect=ToolSideEffect.EXTERNAL,
        resource_scope=ToolScope.EXTERNAL,
    )
    decision = PolicyEvaluator().evaluate(request, definition, now=BASE_TIME)
    assert decision.outcome is PolicyDecisionOutcome.ASK
    assert decision.rule_id == "policy.resource.external"


def test_protected_target_is_denied_even_for_high_risk_request(
    tmp_path: Path,
) -> None:
    """A protected workspace target remains denied despite elevated risk."""
    root = tmp_path / "workspace"
    (root / ".git").mkdir(parents=True)
    request = make_request(
        root=root,
        autonomy_mode=AutonomyMode.ASSISTED_IMPLEMENT,
        risk_level=ToolRiskLevel.HIGH,
        arguments={"path": ".git"},
    )
    definition = make_definition(
        risk_level=ToolRiskLevel.HIGH,
        side_effect=ToolSideEffect.DESTRUCTIVE,
        resource_scope=ToolScope.WORKSPACE,
    )
    decision = PolicyEvaluator().evaluate(request, definition, now=BASE_TIME)
    assert decision.outcome is PolicyDecisionOutcome.DENY
    assert decision.rule_id == "policy.resource.protected"
