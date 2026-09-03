"""Contract tests for client/runtime protocol messages."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from coagent.core.types import EventSeverity
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    EventType,
    ProtocolMessage,
    RequestType,
    RuntimeEvent,
)


def test_client_request_validates() -> None:
    request_id = uuid4()
    session_id = uuid4()
    task_id = uuid4()
    created_at = datetime.now(UTC)

    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        session_id=session_id,
        task_id=task_id,
        type=RequestType.TASK_CREATE,
        payload={"name": "example"},
        client_context={"workspace": "test"},
        created_at=created_at,
    )

    assert request.protocol_version == PROTOCOL_VERSION
    assert request.request_id == request_id
    assert request.session_id == session_id
    assert request.task_id == task_id
    assert request.type is RequestType.TASK_CREATE
    assert request.payload == {"name": "example"}
    assert request.client_context == {"workspace": "test"}
    assert request.created_at == created_at


def test_runtime_event_validates() -> None:
    event_id = uuid4()
    request_id = uuid4()
    session_id = uuid4()
    task_id = uuid4()
    created_at = datetime.now(UTC)

    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=event_id,
        request_id=request_id,
        session_id=session_id,
        task_id=task_id,
        type=EventType.TASK_CREATED,
        payload={"name": "example"},
        severity=EventSeverity.INFO,
        created_at=created_at,
    )

    assert event.protocol_version == PROTOCOL_VERSION
    assert event.event_id == event_id
    assert event.request_id == request_id
    assert event.session_id == session_id
    assert event.task_id == task_id
    assert event.type is EventType.TASK_CREATED
    assert event.payload == {"name": "example"}
    assert event.severity is EventSeverity.INFO
    assert event.created_at == created_at


def test_runtime_event_allows_null_request_and_task_ids() -> None:
    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        request_id=None,
        session_id=uuid4(),
        task_id=None,
        type=EventType.CONTEXT_UPDATED,
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )

    assert event.request_id is None
    assert event.task_id is None


def test_protocol_version_is_required() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(  # type: ignore[call-arg]
            request_id=uuid4(),
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            created_at=datetime.now(UTC),
        )


def test_unsupported_protocol_version_is_rejected() -> None:
    with pytest.raises(ValidationError, match="unsupported protocol version"):
        ClientRequest(
            protocol_version="999.0",
            request_id=uuid4(),
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            created_at=datetime.now(UTC),
        )


def test_unknown_request_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=uuid4(),
            type="unknown.request",  # type: ignore[arg-type]
            created_at=datetime.now(UTC),
        )


def test_unknown_event_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RuntimeEvent(
            protocol_version=PROTOCOL_VERSION,
            event_id=uuid4(),
            session_id=uuid4(),
            type="unknown.event",  # type: ignore[arg-type]
            severity=EventSeverity.INFO,
            created_at=datetime.now(UTC),
        )


def test_invalid_uuid_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id="not-a-uuid",  # type: ignore[arg-type]
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            created_at=datetime.now(UTC),
        )


def test_payload_must_be_object() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            payload=["not", "an", "object"],  # type: ignore[arg-type]
            created_at=datetime.now(UTC),
        )


def test_client_context_must_be_object() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            client_context=["not", "an", "object"],  # type: ignore[arg-type]
            created_at=datetime.now(UTC),
        )


def test_unknown_client_request_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=uuid4(),
            type=RequestType.TASK_STATUS,
            created_at=datetime.now(UTC),
            unexpected="value",  # type: ignore[call-arg]
        )


def test_unknown_runtime_event_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        RuntimeEvent(
            protocol_version=PROTOCOL_VERSION,
            event_id=uuid4(),
            session_id=uuid4(),
            type=EventType.TASK_CREATED,
            severity=EventSeverity.INFO,
            created_at=datetime.now(UTC),
            unexpected="value",  # type: ignore[call-arg]
        )


def test_protocol_message_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProtocolMessage(
            protocol_version=PROTOCOL_VERSION,
            unexpected="value",  # type: ignore[call-arg]
        )


def test_client_request_json_roundtrip() -> None:
    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=RequestType.TASK_CREATE,
        payload={"key": "value"},
        client_context={"client": "vscode"},
        created_at=datetime.now(UTC),
    )

    restored = ClientRequest.model_validate_json(request.model_dump_json())

    assert restored == request


def test_runtime_event_json_roundtrip() -> None:
    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=EventType.TASK_COMPLETED,
        payload={"status": "complete"},
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )

    restored = RuntimeEvent.model_validate_json(event.model_dump_json())

    assert restored == event


def test_client_request_correlation_ids_are_preserved() -> None:
    request_id = uuid4()
    session_id = uuid4()
    task_id = uuid4()

    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        session_id=session_id,
        task_id=task_id,
        type=RequestType.TASK_STATUS,
        created_at=datetime.now(UTC),
    )

    assert request.request_id == request_id
    assert request.session_id == session_id
    assert request.task_id == task_id


def test_runtime_event_correlation_ids_are_preserved() -> None:
    event_id = uuid4()
    request_id = uuid4()
    session_id = uuid4()
    task_id = uuid4()

    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=event_id,
        request_id=request_id,
        session_id=session_id,
        task_id=task_id,
        type=EventType.TASK_STATE_CHANGED,
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )

    assert event.event_id == event_id
    assert event.request_id == request_id
    assert event.session_id == session_id
    assert event.task_id == task_id


@pytest.mark.parametrize("request_type", list(RequestType))
def test_all_request_types_are_supported(request_type: RequestType) -> None:
    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=uuid4(),
        type=request_type,
        created_at=datetime.now(UTC),
    )

    assert request.type is request_type


@pytest.mark.parametrize("event_type", list(EventType))
def test_all_event_types_are_supported(event_type: EventType) -> None:
    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        session_id=uuid4(),
        type=event_type,
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )

    assert event.type is event_type


def test_uuid_fields_are_typed() -> None:
    request = ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=str(uuid4()),  # type: ignore[arg-type]
        session_id=str(uuid4()),  # type: ignore[arg-type]
        type=RequestType.TASK_STATUS,
        created_at=datetime.now(UTC),
    )

    assert isinstance(request.request_id, UUID)
    assert isinstance(request.session_id, UUID)


@pytest.mark.parametrize("severity", list(EventSeverity))
def test_all_event_severities_are_supported(severity: EventSeverity) -> None:
    event = RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        session_id=uuid4(),
        type=EventType.TASK_CREATED,
        severity=severity,
        created_at=datetime.now(UTC),
    )

    assert event.severity is severity
