"""Contract and serialization tests for core runtime models."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from coagent.core.errors import ErrorRecord
from coagent.core.events import EventEnvelope
from coagent.core.ids import (
    generate_event_id,
    generate_request_id,
    generate_session_id,
    generate_task_id,
)
from coagent.core.result import Result
from coagent.core.types import EventSeverity, Recoverability
from coagent.protocol.errors import (
    ProtocolError,
    ProtocolErrorCode,
    ProtocolErrorEnvelope,
)
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    EventType,
    RequestType,
    RuntimeEvent,
)
from coagent.runtime.session import Session, SessionState
from coagent.runtime.task_state import TaskState


def make_error(
    *,
    task_id: UUID | None = None,
    correlation_id: UUID | None = None,
) -> ErrorRecord:
    now = datetime.now(UTC)

    return ErrorRecord(
        error_id=uuid4(),
        task_id=task_id,
        correlation_id=correlation_id or uuid4(),
        category="TEST",
        code="TEST-001",
        source="contract-test",
        message="test failure",
        severity=EventSeverity.ERROR,
        recoverability=Recoverability.AUTO,
        evidence_refs=["evidence://test"],
        affected_scope={"scope": "test"},
        retry_key="retry-test",
        occurred_at=now,
        normalized_at=now,
    )


def make_client_request(
    request_type: RequestType = RequestType.TASK_CREATE,
) -> ClientRequest:
    return ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=request_type,
        payload={
            "name": "example",
            "options": {"enabled": True},
        },
        client_context={
            "client": "vscode",
            "version": "test",
        },
        created_at=datetime.now(UTC),
    )


def make_runtime_event(
    event_type: EventType = EventType.TASK_COMPLETED,
) -> RuntimeEvent:
    return RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=event_type,
        payload={
            "status": "complete",
            "metadata": {"source": "test"},
        },
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Stable IDs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "generator",
    [
        generate_session_id,
        generate_task_id,
        generate_request_id,
        generate_event_id,
    ],
)
def test_generated_ids_are_uuid_instances(generator) -> None:
    value = generator()

    assert isinstance(value, UUID)
    assert value is not None


def test_generated_ids_are_unique_across_repeated_generation() -> None:
    generated = {
        generate_session_id()
        for _ in range(25)
    }

    assert len(generated) == 25


# ---------------------------------------------------------------------------
# Enum wire values
# ---------------------------------------------------------------------------


def test_event_severity_wire_values_are_stable() -> None:
    assert [value.value for value in EventSeverity] == [
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]


def test_recoverability_wire_values_are_stable() -> None:
    assert [value.value for value in Recoverability] == [
        "AUTO",
        "ASSISTED",
        "MANUAL",
        "NONE",
    ]


# ---------------------------------------------------------------------------
# ErrorRecord
# ---------------------------------------------------------------------------


def test_error_record_json_roundtrip_preserves_all_fields() -> None:
    error = make_error(task_id=uuid4())

    restored = ErrorRecord.model_validate_json(
        error.model_dump_json()
    )

    assert restored == error
    assert restored.error_id == error.error_id
    assert restored.task_id == error.task_id
    assert restored.correlation_id == error.correlation_id
    assert restored.severity is error.severity
    assert restored.recoverability is error.recoverability
    assert restored.evidence_refs == error.evidence_refs
    assert restored.affected_scope == error.affected_scope
    assert restored.retry_key == error.retry_key
    assert restored.occurred_at == error.occurred_at
    assert restored.normalized_at == error.normalized_at


def test_error_record_json_roundtrip_preserves_null_task_id() -> None:
    error = make_error(task_id=None)

    restored = ErrorRecord.model_validate_json(
        error.model_dump_json()
    )

    assert restored == error
    assert restored.task_id is None


@pytest.mark.parametrize("severity", list(EventSeverity))
def test_error_record_roundtrip_preserves_severity(
    severity: EventSeverity,
) -> None:
    error = make_error().model_copy(
        update={"severity": severity}
    )

    restored = ErrorRecord.model_validate_json(
        error.model_dump_json()
    )

    assert restored.severity is severity


@pytest.mark.parametrize("recoverability", list(Recoverability))
def test_error_record_roundtrip_preserves_recoverability(
    recoverability: Recoverability,
) -> None:
    error = make_error().model_copy(
        update={"recoverability": recoverability}
    )

    restored = ErrorRecord.model_validate_json(
        error.model_dump_json()
    )

    assert restored.recoverability is recoverability


def test_error_record_rejects_malformed_uuid() -> None:
    with pytest.raises(ValidationError):
        ErrorRecord(
            error_id="not-a-uuid",  # type: ignore[arg-type]
            correlation_id=uuid4(),
            category="TEST",
            code="TEST-001",
            source="contract-test",
            message="test failure",
            severity=EventSeverity.ERROR,
            recoverability=Recoverability.NONE,
            occurred_at=datetime.now(UTC),
            normalized_at=datetime.now(UTC),
        )


# ---------------------------------------------------------------------------
# EventEnvelope
# ---------------------------------------------------------------------------


def test_event_envelope_json_roundtrip_preserves_all_fields() -> None:
    event = EventEnvelope(
        event_id=uuid4(),
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type="TASK_STARTED",
        severity=EventSeverity.WARNING,
        timestamp=datetime.now(UTC),
        source="contract-test",
        payload={
            "message": "started",
            "metadata": {"attempt": 1},
        },
    )

    restored = EventEnvelope.model_validate_json(
        event.model_dump_json()
    )

    assert restored == event
    assert restored.event_id == event.event_id
    assert restored.request_id == event.request_id
    assert restored.session_id == event.session_id
    assert restored.task_id == event.task_id
    assert restored.severity is event.severity
    assert restored.timestamp == event.timestamp
    assert restored.source == event.source
    assert restored.payload == event.payload


def test_event_envelope_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_id=uuid4(),
            request_id=uuid4(),
            session_id=uuid4(),
            task_id=uuid4(),
            type="TEST",
            severity=EventSeverity.INFO,
            timestamp=datetime.now(UTC),
            source="contract-test",
            payload={},
            unexpected="value",  # type: ignore[call-arg]
        )


# ---------------------------------------------------------------------------
# Result[T]
# ---------------------------------------------------------------------------


def test_success_result_json_roundtrip_preserves_result() -> None:
    request_id = uuid4()

    result = Result[str](
        request_id=request_id,
        success=True,
        result="success-value",
    )

    restored = Result[str].model_validate_json(
        result.model_dump_json()
    )

    assert restored == result
    assert restored.request_id == request_id
    assert restored.success is True
    assert restored.result == "success-value"
    assert restored.error is None


def test_failure_result_json_roundtrip_preserves_error() -> None:
    request_id = uuid4()
    error = make_error()

    result = Result[str](
        request_id=request_id,
        success=False,
        error=error,
    )

    restored = Result[str].model_validate_json(
        result.model_dump_json()
    )

    assert restored == result
    assert restored.request_id == request_id
    assert restored.success is False
    assert restored.result is None
    assert restored.error == error


def test_result_rejects_invalid_json() -> None:
    with pytest.raises(ValidationError):
        Result[str].model_validate_json(
            '{"request_id":"not-a-uuid","success":true,"result":"ok"}'
        )


def test_result_rejects_wrong_top_level_json_shape() -> None:
    with pytest.raises(ValidationError):
        Result[str].model_validate_json("[]")


# ---------------------------------------------------------------------------
# Session contract
# ---------------------------------------------------------------------------


def test_session_identity_is_stable_across_lifecycle_changes() -> None:
    session = Session()
    session_id = session.session_id

    session.disconnect()
    assert session.session_id == session_id
    assert session.state is SessionState.DISCONNECTED

    session.reconnect()
    assert session.session_id == session_id
    assert session.state is SessionState.ACTIVE


def test_session_state_wire_values_are_stable() -> None:
    assert [state.value for state in SessionState] == [
        "ACTIVE",
        "DISCONNECTED",
        "TERMINATED",
    ]


# ---------------------------------------------------------------------------
# Task state contract
# ---------------------------------------------------------------------------


def test_task_state_wire_values_are_stable() -> None:
    assert [state.value for state in TaskState] == [
        "CREATED",
        "PLANNING",
        "READY",
        "IMPLEMENTING",
        "VALIDATING",
        "RECOVERING",
        "BLOCKED",
        "FAILED",
        "COMPLETE",
        "CANCELLED",
    ]


# ---------------------------------------------------------------------------
# ClientRequest serialization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("request_type", list(RequestType))
def test_client_request_all_types_json_roundtrip(
    request_type: RequestType,
) -> None:
    request = make_client_request(request_type)

    restored = ClientRequest.model_validate_json(
        request.model_dump_json()
    )

    assert restored == request
    assert restored.protocol_version == PROTOCOL_VERSION
    assert restored.request_id == request.request_id
    assert restored.session_id == request.session_id
    assert restored.task_id == request.task_id
    assert restored.type is request_type
    assert restored.payload == request.payload
    assert restored.client_context == request.client_context
    assert restored.created_at == request.created_at


def test_client_request_empty_payload_and_context_roundtrip() -> None:
    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=None,
        type=RequestType.TASK_STATUS,
        payload={},
        client_context={},
        created_at=datetime.now(UTC),
    )

    restored = ClientRequest.model_validate_json(
        request.model_dump_json()
    )

    assert restored == request
    assert restored.payload == {}
    assert restored.client_context == {}
    assert restored.task_id is None


# ---------------------------------------------------------------------------
# RuntimeEvent serialization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("event_type", list(EventType))
def test_runtime_event_all_types_json_roundtrip(
    event_type: EventType,
) -> None:
    event = make_runtime_event(event_type)

    restored = RuntimeEvent.model_validate_json(
        event.model_dump_json()
    )

    assert restored == event
    assert restored.protocol_version == PROTOCOL_VERSION
    assert restored.event_id == event.event_id
    assert restored.request_id == event.request_id
    assert restored.session_id == event.session_id
    assert restored.task_id == event.task_id
    assert restored.type is event_type
    assert restored.payload == event.payload
    assert restored.severity is event.severity
    assert restored.created_at == event.created_at


def test_runtime_event_nullable_correlation_ids_roundtrip() -> None:
    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        request_id=None,
        session_id=uuid4(),
        task_id=None,
        type=EventType.CONTEXT_UPDATED,
        payload={},
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )

    restored = RuntimeEvent.model_validate_json(
        event.model_dump_json()
    )

    assert restored == event
    assert restored.request_id is None
    assert restored.task_id is None


# ---------------------------------------------------------------------------
# ProtocolError / ProtocolErrorEnvelope serialization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", list(ProtocolErrorCode))
def test_protocol_error_json_roundtrip_preserves_code(
    code: ProtocolErrorCode,
) -> None:
    canonical_messages = {
        ProtocolErrorCode.MALFORMED_MESSAGE: "Malformed protocol message.",
        ProtocolErrorCode.UNSUPPORTED_PROTOCOL_VERSION: (
            "Unsupported protocol version."
        ),
        ProtocolErrorCode.INVALID_REQUEST: "Invalid request.",
        ProtocolErrorCode.UNKNOWN_REQUEST_TYPE: "Unknown request type.",
        ProtocolErrorCode.MISSING_REQUIRED_FIELD: "Missing required field.",
        ProtocolErrorCode.INVALID_FIELD: "Invalid field.",
        ProtocolErrorCode.INVALID_FIELD_TYPE: "Invalid field type.",
        ProtocolErrorCode.INVALID_CORRELATION_ID: (
            "Invalid correlation ID."
        ),
        ProtocolErrorCode.PAYLOAD_INVALID: "Invalid payload.",
    }

    error = ProtocolError(
        code=code,
        message=canonical_messages[code],
        request_id=uuid4(),
        details={
            "field": "payload",
            "reason": "invalid",
        },
    )

    restored = ProtocolError.model_validate_json(
        error.model_dump_json()
    )

    assert restored == error
    assert restored.code is code
    assert restored.message == error.message
    assert restored.request_id == error.request_id
    assert restored.details == error.details


def test_protocol_error_envelope_json_roundtrip_preserves_nested_contract() -> None:
    request_id = uuid4()

    envelope = ProtocolErrorEnvelope(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        error=ProtocolError(
            code=ProtocolErrorCode.INVALID_FIELD,
            message="Invalid field.",
            request_id=request_id,
            details={
                "field": "session_id",
                "reason": "invalid UUID",
            },
        ),
        created_at=datetime.now(UTC),
    )

    restored = ProtocolErrorEnvelope.model_validate_json(
        envelope.model_dump_json()
    )

    assert restored == envelope
    assert restored.protocol_version == PROTOCOL_VERSION
    assert restored.request_id == request_id
    assert restored.error.request_id == request_id
    assert restored.error.code is ProtocolErrorCode.INVALID_FIELD
    assert restored.error.details == envelope.error.details
    assert restored.created_at == envelope.created_at


# ---------------------------------------------------------------------------
# Malformed JSON / invalid structures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw_json",
    [
        "",
        "not-json",
        "{",
        "[]",
        '"string"',
        "123",
        "null",
    ],
)
def test_client_request_rejects_malformed_or_wrong_top_level_json(
    raw_json: str,
) -> None:
    with pytest.raises((ValidationError, ValueError)):
        ClientRequest.model_validate_json(raw_json)


@pytest.mark.parametrize(
    "raw_json",
    [
        "",
        "not-json",
        "{",
        "[]",
        '"string"',
        "123",
        "null",
    ],
)
def test_runtime_event_rejects_malformed_or_wrong_top_level_json(
    raw_json: str,
) -> None:
    with pytest.raises((ValidationError, ValueError)):
        RuntimeEvent.model_validate_json(raw_json)


def test_client_request_rejects_missing_required_field_after_serialization_boundary() -> None:
    raw_json = """
    {
        "protocol_version": "1.0",
        "request_id": "00000000-0000-0000-0000-000000000001",
        "session_id": "00000000-0000-0000-0000-000000000002",
        "type": "task.status",
        "payload": {},
        "client_context": {}
    }
    """

    with pytest.raises(ValidationError):
        ClientRequest.model_validate_json(raw_json)


def test_runtime_event_rejects_invalid_enum_after_serialization_boundary() -> None:
    raw_json = """
    {
        "protocol_version": "1.0",
        "event_id": "00000000-0000-0000-0000-000000000001",
        "session_id": "00000000-0000-0000-0000-000000000002",
        "type": "unknown.event",
        "payload": {},
        "severity": "INFO",
        "created_at": "2026-01-01T00:00:00Z"
    }
    """

    with pytest.raises(ValidationError):
        RuntimeEvent.model_validate_json(raw_json)


def test_client_request_rejects_non_object_payload_after_serialization_boundary() -> None:
    raw_json = """
    {
        "protocol_version": "1.0",
        "request_id": "00000000-0000-0000-0000-000000000001",
        "session_id": "00000000-0000-0000-0000-000000000002",
        "type": "task.status",
        "payload": [],
        "client_context": {},
        "created_at": "2026-01-01T00:00:00Z"
    }
    """

    with pytest.raises(ValidationError):
        ClientRequest.model_validate_json(raw_json)


def test_protocol_error_envelope_rejects_invalid_nested_error() -> None:
    raw_json = """
    {
        "protocol_version": "1.0",
        "request_id": null,
        "error": {
            "code": "INVALID_REQUEST",
            "message": "Invalid request.",
            "request_id": "not-a-uuid",
            "details": {}
        },
        "created_at": "2026-01-01T00:00:00Z"
    }
    """

    with pytest.raises(ValidationError):
        ProtocolErrorEnvelope.model_validate_json(raw_json)


def test_protocol_error_envelope_rejects_extra_nested_fields() -> None:
    raw_json = """
    {
        "protocol_version": "1.0",
        "request_id": null,
        "error": {
            "code": "INVALID_REQUEST",
            "message": "Invalid request.",
            "details": {},
            "unexpected": "value"
        },
        "created_at": "2026-01-01T00:00:00Z"
    }
    """

    with pytest.raises(ValidationError):
        ProtocolErrorEnvelope.model_validate_json(raw_json)


def test_serialization_preserves_uuid_and_datetime_types() -> None:
    created_at = datetime.now(UTC)
    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=RequestType.TASK_STATUS,
        payload={},
        client_context={},
        created_at=created_at,
    )

    restored = ClientRequest.model_validate_json(
        request.model_dump_json()
    )

    assert isinstance(restored.request_id, UUID)
    assert isinstance(restored.session_id, UUID)
    assert isinstance(restored.task_id, UUID)
    assert isinstance(restored.created_at, datetime)
    assert restored.created_at == created_at