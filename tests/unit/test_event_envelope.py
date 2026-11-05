"""Unit tests for EventEnvelope and canonical event types (T087)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.core.events import EventEnvelope, EventType
from coagent.core.types import EventSeverity


def test_event_envelope_factory_create() -> None:
    task_id = uuid4()
    session_id = uuid4()
    corr_id = uuid4()

    event = EventEnvelope.create(
        event_type=EventType.TASK_CREATED,
        task_id=task_id,
        session_id=session_id,
        payload={"goal": "Refactor parser"},
        correlation_id=corr_id,
        severity=EventSeverity.INFO,
        source="orchestrator",
    )

    assert event.type == EventType.TASK_CREATED.value
    assert event.task_id == task_id
    assert event.session_id == session_id
    assert event.correlation_id == corr_id
    assert event.payload == {"goal": "Refactor parser"}
    assert event.severity == EventSeverity.INFO
    assert event.source == "orchestrator"
    assert isinstance(event.timestamp, datetime)


def test_event_envelope_defaults_correlation_id_to_request_id() -> None:
    task_id = uuid4()
    session_id = uuid4()
    req_id = uuid4()

    event = EventEnvelope.create(
        event_type="CUSTOM_EVENT",
        task_id=task_id,
        session_id=session_id,
        request_id=req_id,
        payload={"step": 1},
    )

    assert event.request_id == req_id
    assert event.correlation_id == req_id


def test_event_envelope_serialization_roundtrip() -> None:
    event = EventEnvelope.create(
        event_type=EventType.VALIDATION_STARTED,
        task_id=uuid4(),
        session_id=uuid4(),
        payload={"gate": "pytest"},
    )

    serialized = event.model_dump_json()
    deserialized = EventEnvelope.model_validate_json(serialized)

    assert deserialized == event
    assert deserialized.correlation_id == event.correlation_id


def test_event_envelope_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_id=uuid4(),
            request_id=uuid4(),
            session_id=uuid4(),
            task_id=uuid4(),
            type="TEST",
            severity=EventSeverity.INFO,
            timestamp=datetime.now(UTC),
            source="test",
            payload={},
            unexpected_field="disallowed",  # type: ignore[call-arg]
        )
