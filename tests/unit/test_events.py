from datetime import UTC, datetime
from uuid import uuid4

from coagent.core.events import EventEnvelope
from coagent.core.types import EventSeverity


def test_event_envelope_contains_required_fields() -> None:
    event_id = uuid4()
    request_id = uuid4()
    session_id = uuid4()
    task_id = uuid4()
    timestamp = datetime.now(UTC)
    event = EventEnvelope(
        event_id=event_id,
        request_id=request_id,
        session_id=session_id,
        task_id=task_id,
        type="TASK_STARTED",
        severity=EventSeverity.INFO,
        timestamp=timestamp,
        source="runtime",
        payload={"message": "started"},
    )
    assert event.event_id == event_id
    assert event.request_id == request_id
    assert event.session_id == session_id
    assert event.task_id == task_id
    assert event.type == "TASK_STARTED"
    assert event.severity is EventSeverity.INFO
    assert event.timestamp == timestamp
    assert event.source == "runtime"
    assert event.payload == {"message": "started"}


def test_event_envelope_accepts_arbitrary_payload() -> None:
    event = EventEnvelope(
        event_id=uuid4(),
        request_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type="TEST",
        severity=EventSeverity.WARNING,
        timestamp=datetime.now(UTC),
        source="unit-test",
        payload=["a", "b"],
    )
    assert event.severity is EventSeverity.WARNING
    assert event.payload == ["a", "b"]
