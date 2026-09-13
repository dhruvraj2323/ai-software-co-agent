"""Unit tests for the canonical approval lifecycle."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.policy.approval import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    ApprovalStore,
)
from coagent.tools.registry import ToolRiskLevel

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def make_request() -> ApprovalRequest:
    return ApprovalRequest(
        approval_id=uuid4(),
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="terminal.powershell",
        action="run test command",
        target="/workspace/project",
        risk_level=ToolRiskLevel.HIGH,
        reason="The requested operation requires human authorization.",
        alternatives=["Use a read-only inspection command."],
        expires_at=BASE_TIME + timedelta(minutes=10),
        created_at=BASE_TIME,
    )


def test_new_approval_starts_pending() -> None:
    request = make_request()
    store = ApprovalStore()
    record = store.create(request)
    assert record.status is ApprovalStatus.PENDING
    assert record.decision is None
    assert record.decided_at is None
    assert record.may_continue is False


def test_approve_moves_pending_to_approved() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    record = store.decide(
        request.approval_id,
        request.request_id,
        ApprovalDecision.APPROVE,
        BASE_TIME + timedelta(minutes=1),
    )
    assert record.status is ApprovalStatus.APPROVED
    assert record.decision is ApprovalDecision.APPROVE
    assert record.decided_at == BASE_TIME + timedelta(minutes=1)
    assert record.may_continue is True


def test_reject_moves_pending_to_rejected() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    record = store.decide(
        request.approval_id,
        request.request_id,
        ApprovalDecision.REJECT,
        BASE_TIME + timedelta(minutes=1),
    )
    assert record.status is ApprovalStatus.REJECTED
    assert record.decision is ApprovalDecision.REJECT
    assert record.may_continue is False


def test_expiry_moves_pending_to_expired() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    record = store.expire(
        request.approval_id,
        request.request_id,
        request.expires_at,
    )
    assert record.status is ApprovalStatus.EXPIRED
    assert record.decision is None
    assert record.may_continue is False


def test_decision_after_expiry_is_not_allowed() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    with pytest.raises(ValueError, match="approval has expired"):
        store.decide(
            request.approval_id,
            request.request_id,
            ApprovalDecision.APPROVE,
            request.expires_at,
        )
    record = store.get(request.approval_id)
    assert record.status is ApprovalStatus.EXPIRED
    assert record.may_continue is False


def test_approved_record_cannot_be_reused() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    store.decide(
        request.approval_id,
        request.request_id,
        ApprovalDecision.APPROVE,
        BASE_TIME + timedelta(minutes=1),
    )
    with pytest.raises(ValueError, match="approval is not pending"):
        store.decide(
            request.approval_id,
            request.request_id,
            ApprovalDecision.REJECT,
            BASE_TIME + timedelta(minutes=2),
        )


def test_rejected_record_cannot_be_reused() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    store.decide(
        request.approval_id,
        request.request_id,
        ApprovalDecision.REJECT,
        BASE_TIME + timedelta(minutes=1),
    )
    with pytest.raises(ValueError, match="approval is not pending"):
        store.decide(
            request.approval_id,
            request.request_id,
            ApprovalDecision.APPROVE,
            BASE_TIME + timedelta(minutes=2),
        )


def test_expired_record_cannot_be_reused() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    store.expire(
        request.approval_id,
        request.request_id,
        request.expires_at,
    )
    with pytest.raises(ValueError, match="approval is not pending"):
        store.expire(
            request.approval_id,
            request.request_id,
            request.expires_at + timedelta(minutes=1),
        )


def test_wrong_request_cannot_consume_approval() -> None:
    request = make_request()
    different_request_id = uuid4()
    store = ApprovalStore()
    store.create(request)
    with pytest.raises(ValueError, match="not bound"):
        store.decide(
            request.approval_id,
            different_request_id,
            ApprovalDecision.APPROVE,
            BASE_TIME + timedelta(minutes=1),
        )
    assert store.get(request.approval_id).status is ApprovalStatus.PENDING


def test_duplicate_approval_id_is_rejected() -> None:
    request = make_request()
    store = ApprovalStore()
    store.create(request)
    with pytest.raises(ValueError, match="approval already exists"):
        store.create(request)


def test_unknown_approval_id_is_rejected() -> None:
    store = ApprovalStore()
    with pytest.raises(KeyError, match="unknown approval"):
        store.get(uuid4())


def test_approval_request_rejects_extra_fields() -> None:
    values = make_request().model_dump()
    values["unexpected"] = "not allowed"
    with pytest.raises(ValidationError):
        ApprovalRequest.model_validate(values)


def test_approval_request_round_trips_through_json() -> None:
    request = make_request()
    restored = ApprovalRequest.model_validate_json(request.model_dump_json())
    assert restored == request


def test_approval_request_is_immutable() -> None:
    request = make_request()
    with pytest.raises(ValidationError):
        request.tool_id = "workspace.delete"  # type: ignore[misc]
