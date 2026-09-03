from datetime import UTC
from uuid import uuid4

import pytest

from coagent.core.errors import ErrorRecord
from coagent.core.result import Result
from coagent.core.types import EventSeverity, Recoverability


def make_error() -> ErrorRecord:
    from datetime import datetime

    now = datetime.now(UTC)
    return ErrorRecord(
        error_id=uuid4(),
        correlation_id=uuid4(),
        category="TEST",
        code="TEST-001",
        source="unit-test",
        message="test failure",
        severity=EventSeverity.ERROR,
        recoverability=Recoverability.NONE,
        occurred_at=now,
        normalized_at=now,
    )


def test_success_result_contains_typed_result() -> None:
    request_id = uuid4()
    result = Result[str](
        request_id=request_id,
        success=True,
        result="ok",
    )
    assert result.request_id == request_id
    assert result.success is True
    assert result.result == "ok"
    assert result.error is None


def test_failure_result_contains_error() -> None:
    result = Result[str](
        request_id=uuid4(),
        success=False,
        error=make_error(),
    )
    assert result.success is False
    assert result.result is None
    assert result.error is not None


def test_success_result_requires_result() -> None:
    with pytest.raises(ValueError, match="must contain a result"):
        Result[str](
            request_id=uuid4(),
            success=True,
        )


def test_failure_result_requires_error() -> None:
    with pytest.raises(ValueError, match="must contain an error"):
        Result[str](
            request_id=uuid4(),
            success=False,
        )


def test_success_result_rejects_error() -> None:
    with pytest.raises(ValueError, match="cannot contain an error"):
        Result[str](
            request_id=uuid4(),
            success=True,
            result="ok",
            error=make_error(),
        )


def test_failure_result_rejects_result() -> None:
    with pytest.raises(ValueError, match="cannot contain a result"):
        Result[str](
            request_id=uuid4(),
            success=False,
            result="unexpected",
            error=make_error(),
        )
