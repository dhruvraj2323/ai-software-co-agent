"""Contract tests for the minimal runtime service."""

from datetime import UTC, datetime
from uuid import uuid4

from coagent.protocol.errors import ProtocolErrorCode, ProtocolErrorEnvelope
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    EventType,
    RequestType,
    RuntimeEvent,
)
from coagent.runtime.service import RuntimeService
from coagent.runtime.task_state import TaskState


def make_request(
    request_type: RequestType,
    *,
    session_id=None,
    task_id=None,
    payload=None,
) -> ClientRequest:
    """Create a valid protocol request for runtime-service tests."""
    return ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=session_id or uuid4(),
        task_id=task_id,
        type=request_type,
        payload=payload or {},
        client_context={},
        created_at=datetime.now(UTC),
    )


def test_health_returns_healthy_runtime() -> None:
    service = RuntimeService()

    assert service.health() == {
        "status": "healthy",
        "protocol_version": PROTOCOL_VERSION,
    }


def test_session_start_creates_runtime_session() -> None:
    service = RuntimeService()
    session_id = uuid4()
    request = make_request(
        RequestType.SESSION_START,
        session_id=session_id,
    )

    response = service.handle(request)

    assert isinstance(response, RuntimeEvent)
    assert response.type is EventType.CONTEXT_UPDATED
    assert response.session_id == session_id
    assert response.request_id == request.request_id
    assert response.payload["session_id"] == str(session_id)
    assert response.payload["state"] == "ACTIVE"


def test_session_start_is_idempotent_for_existing_session() -> None:
    service = RuntimeService()
    session_id = uuid4()

    first = service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )
    second = service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    assert isinstance(first, RuntimeEvent)
    assert isinstance(second, RuntimeEvent)
    assert first.session_id == second.session_id == session_id
    assert first.payload["state"] == second.payload["state"] == "ACTIVE"


def test_task_create_requires_existing_session() -> None:
    service = RuntimeService()
    session_id = uuid4()

    response = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
        )
    )

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.INVALID_CORRELATION_ID


def test_task_create_generates_task_id() -> None:
    service = RuntimeService()
    session_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    response = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
        )
    )

    assert isinstance(response, RuntimeEvent)
    assert response.type is EventType.TASK_CREATED
    assert response.task_id is not None
    assert response.payload["task_id"] == str(response.task_id)
    assert response.payload["session_id"] == str(session_id)
    assert response.payload["state"] == TaskState.CREATED.value


def test_task_create_preserves_supplied_task_id() -> None:
    service = RuntimeService()
    session_id = uuid4()
    task_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    response = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
            task_id=task_id,
        )
    )

    assert isinstance(response, RuntimeEvent)
    assert response.task_id == task_id
    assert response.payload["task_id"] == str(task_id)


def test_task_create_starts_task_in_created_state() -> None:
    service = RuntimeService()
    session_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    created = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
        )
    )

    assert isinstance(created, RuntimeEvent)
    assert created.task_id is not None

    status = service.handle(
        make_request(
            RequestType.TASK_STATUS,
            session_id=session_id,
            task_id=created.task_id,
        )
    )

    assert isinstance(status, RuntimeEvent)
    assert status.type is EventType.TASK_STATE_CHANGED
    assert status.task_id == created.task_id
    assert status.payload["state"] == TaskState.CREATED.value


def test_task_status_requires_task_id() -> None:
    service = RuntimeService()
    session_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    response = service.handle(
        make_request(
            RequestType.TASK_STATUS,
            session_id=session_id,
        )
    )

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.MISSING_REQUIRED_FIELD


def test_task_status_rejects_unknown_task() -> None:
    service = RuntimeService()
    session_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    response = service.handle(
        make_request(
            RequestType.TASK_STATUS,
            session_id=session_id,
            task_id=uuid4(),
        )
    )

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.INVALID_CORRELATION_ID


def test_task_status_rejects_cross_session_access() -> None:
    service = RuntimeService()
    owner_session_id = uuid4()
    other_session_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=owner_session_id,
        )
    )
    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=other_session_id,
        )
    )

    created = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=owner_session_id,
        )
    )

    assert isinstance(created, RuntimeEvent)
    assert created.task_id is not None

    response = service.handle(
        make_request(
            RequestType.TASK_STATUS,
            session_id=other_session_id,
            task_id=created.task_id,
        )
    )

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.INVALID_CORRELATION_ID


def test_duplicate_task_id_is_rejected() -> None:
    service = RuntimeService()
    session_id = uuid4()
    task_id = uuid4()

    service.handle(
        make_request(
            RequestType.SESSION_START,
            session_id=session_id,
        )
    )

    first = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
            task_id=task_id,
        )
    )
    second = service.handle(
        make_request(
            RequestType.TASK_CREATE,
            session_id=session_id,
            task_id=task_id,
        )
    )

    assert isinstance(first, RuntimeEvent)
    assert isinstance(second, ProtocolErrorEnvelope)
    assert second.error.code is ProtocolErrorCode.INVALID_REQUEST


def test_unsupported_command_returns_typed_protocol_error() -> None:
    service = RuntimeService()
    session_id = uuid4()

    request = make_request(
        RequestType.TASK_PAUSE,
        session_id=session_id,
    )

    response = service.handle(request)

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.UNKNOWN_REQUEST_TYPE
    assert response.error.request_id == request.request_id


def test_runtime_event_preserves_request_correlation() -> None:
    service = RuntimeService()
    session_id = uuid4()
    request = make_request(
        RequestType.SESSION_START,
        session_id=session_id,
    )

    response = service.handle(request)

    assert isinstance(response, RuntimeEvent)
    assert response.request_id == request.request_id
    assert response.session_id == request.session_id


def test_protocol_error_preserves_request_correlation() -> None:
    service = RuntimeService()
    session_id = uuid4()
    request = make_request(
        RequestType.TASK_STATUS,
        session_id=session_id,
    )

    response = service.handle(request)

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.request_id == request.request_id
    assert response.error.request_id == request.request_id
