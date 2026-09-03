from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability


def make_error() -> ErrorRecord:
    now = datetime.now(UTC)
    return ErrorRecord(
        error_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        category="TEST",
        code="TEST-001",
        source="unit-test",
        message="test failure",
        severity=EventSeverity.ERROR,
        recoverability=Recoverability.AUTO,
        evidence_refs=["evidence://test"],
        occurred_at=now,
        normalized_at=now,
    )


def test_error_record_accepts_required_contract() -> None:
    error = make_error()
    assert error.category == "TEST"
    assert error.code == "TEST-001"
    assert error.evidence_refs == ["evidence://test"]


def test_error_record_rejects_unknown_fields() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        ErrorRecord(
            error_id=uuid4(),
            correlation_id=uuid4(),
            category="TEST",
            code="TEST-001",
            source="unit-test",
            message="test failure",
            severity=EventSeverity.ERROR,
            recoverability=Recoverability.AUTO,
            occurred_at=now,
            normalized_at=now,
            unexpected="value",  # type: ignore[call-arg]
        )


def test_error_record_defaults_optional_fields() -> None:
    error = make_error().model_copy(
        update={"task_id": None, "affected_scope": None, "retry_key": None}
    )
    assert error.task_id is None
    assert error.affected_scope is None
    assert error.retry_key is None
