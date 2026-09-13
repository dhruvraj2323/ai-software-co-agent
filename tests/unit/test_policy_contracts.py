"""Unit tests for canonical policy request and decision contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.policy.contracts import (
    PolicyDecision,
    PolicyDecisionOutcome,
    PolicyRequest,
)
from coagent.tools.contracts import AutonomyMode, Scope, ToolRequestSource
from coagent.tools.registry import ToolRiskLevel


def make_scope() -> Scope:
    return Scope(workspace_id=uuid4(), root="/workspace/project")


def make_request() -> PolicyRequest:
    request_id = uuid4()
    return PolicyRequest(
        request_id=request_id,
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.read",
        tool_version="1.0",
        arguments={"path": "src"},
        requested_scope=make_scope(),
        autonomy_mode=AutonomyMode.ASSISTED_IMPLEMENT,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.LOW,
        created_at=datetime.now(UTC),
    )


def make_decision(
    outcome: PolicyDecisionOutcome = PolicyDecisionOutcome.ALLOW,
) -> PolicyDecision:
    request = make_request()
    return PolicyDecision(
        request_id=request.request_id,
        task_id=request.task_id,
        correlation_id=request.correlation_id,
        outcome=outcome,
        reason="Tool request satisfies the current policy inputs.",
        rule_id="policy.default.allow",
        evaluated_scope=request.requested_scope,
        risk_level=request.risk_level,
        created_at=datetime.now(UTC),
    )


@pytest.mark.parametrize("outcome", list(PolicyDecisionOutcome))
def test_all_policy_outcomes_are_supported(
    outcome: PolicyDecisionOutcome,
) -> None:
    decision = make_decision(outcome)
    assert decision.outcome is outcome


def test_policy_request_validates_canonical_tool_request_inputs() -> None:
    request = make_request()
    assert request.tool_id == "workspace.read"
    assert request.tool_version == "1.0"
    assert request.risk_level is ToolRiskLevel.LOW
    assert request.requested_scope.root == "/workspace/project"


def test_policy_decision_preserves_request_correlation() -> None:
    request = make_request()
    decision = PolicyDecision(
        request_id=request.request_id,
        task_id=request.task_id,
        correlation_id=request.correlation_id,
        outcome=PolicyDecisionOutcome.ASK,
        reason="Additional authorization is required.",
        rule_id="policy.authorization.required",
        evaluated_scope=request.requested_scope,
        risk_level=request.risk_level,
        created_at=datetime.now(UTC),
    )
    assert decision.request_id == request.request_id
    assert decision.task_id == request.task_id
    assert decision.correlation_id == request.correlation_id


def test_policy_decision_contains_required_evidence() -> None:
    decision = make_decision(PolicyDecisionOutcome.RESTRICT)
    assert decision.reason
    assert decision.rule_id
    assert decision.evaluated_scope
    assert decision.risk_level is ToolRiskLevel.LOW


@pytest.mark.parametrize(
    "field",
    ["reason", "rule_id"],
)
def test_policy_decision_rejects_empty_required_evidence(field: str) -> None:
    values = make_decision().model_dump()
    values[field] = ""
    with pytest.raises(ValidationError):
        PolicyDecision.model_validate(values)


def test_policy_decision_rejects_unknown_outcome() -> None:
    values = make_decision().model_dump()
    values["outcome"] = "UNKNOWN"
    with pytest.raises(ValidationError):
        PolicyDecision.model_validate(values)


def test_policy_request_rejects_extra_fields() -> None:
    values = make_request().model_dump()
    values["unexpected"] = "not allowed"
    with pytest.raises(ValidationError):
        PolicyRequest.model_validate(values)


def test_policy_decision_rejects_extra_fields() -> None:
    values = make_decision().model_dump()
    values["unexpected"] = "not allowed"
    with pytest.raises(ValidationError):
        PolicyDecision.model_validate(values)


def test_policy_contracts_round_trip_through_json() -> None:
    request = make_request()
    decision = make_decision(PolicyDecisionOutcome.DENY)
    restored_request = PolicyRequest.model_validate_json(request.model_dump_json())
    restored_decision = PolicyDecision.model_validate_json(decision.model_dump_json())
    assert restored_request == request
    assert restored_decision == decision


def test_policy_contracts_do_not_implement_policy_evaluation() -> None:
    assert not hasattr(PolicyRequest, "evaluate")
    assert not hasattr(PolicyDecision, "evaluate")
