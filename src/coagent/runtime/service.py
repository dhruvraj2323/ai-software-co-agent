"""Minimal runtime service for safe session and task commands."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from coagent.core.ids import generate_event_id, generate_task_id
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
from coagent.runtime.task_state import TaskState, TaskStateMachine

_CANONICAL_MESSAGES: dict[ProtocolErrorCode, str] = {
    ProtocolErrorCode.INVALID_REQUEST: "Invalid request.",
    ProtocolErrorCode.UNKNOWN_REQUEST_TYPE: "Unknown request type.",
    ProtocolErrorCode.MISSING_REQUIRED_FIELD: "Missing required field.",
    ProtocolErrorCode.INVALID_CORRELATION_ID: "Invalid correlation ID.",
}


class RuntimeService:
    """Minimal in-process runtime command service.

    T019 deliberately exposes only safe session/task operations.
    It does not execute tools, processes, filesystem operations, or models.
    """

    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}
        self._tasks: dict[UUID, tuple[UUID, TaskStateMachine]] = {}

    def health(self) -> dict[str, str]:
        """Return deterministic runtime health information."""
        return {
            "status": "healthy",
            "protocol_version": PROTOCOL_VERSION,
        }

    def handle(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Handle one validated client request."""
        if request.type is RequestType.SESSION_START:
            return self._handle_session_start(request)

        if request.type is RequestType.TASK_CREATE:
            return self._handle_task_create(request)

        if request.type is RequestType.TASK_STATUS:
            return self._handle_task_status(request)

        return self._error(
            request,
            ProtocolErrorCode.UNKNOWN_REQUEST_TYPE,
        )

    def _handle_session_start(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Start or reattach a runtime-owned session."""
        session = self._sessions.get(request.session_id)

        if session is None:
            session = Session(session_id=request.session_id)
            self._sessions[request.session_id] = session
        elif session.state is SessionState.TERMINATED:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_REQUEST,
                details={"reason": "session is terminated"},
            )

        return self._event(
            request,
            EventType.CONTEXT_UPDATED,
            {
                "session_id": str(session.session_id),
                "state": session.state.value,
            },
        )

    def _handle_task_create(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Create a task in the CREATED state."""
        session = self._sessions.get(request.session_id)

        if session is None:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_CORRELATION_ID,
                details={"reason": "session does not exist"},
            )

        if session.state is SessionState.TERMINATED:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_REQUEST,
                details={"reason": "session is terminated"},
            )

        if request.task_id is not None and request.task_id in self._tasks:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_REQUEST,
                details={"reason": "task already exists"},
            )

        task_id = request.task_id or generate_task_id()

        self._tasks[task_id] = (
            request.session_id,
            TaskStateMachine(TaskState.CREATED),
        )

        return self._event(
            request,
            EventType.TASK_CREATED,
            {
                "task_id": str(task_id),
                "session_id": str(request.session_id),
                "state": TaskState.CREATED.value,
            },
            task_id=task_id,
        )

    def _handle_task_status(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Return the current state of an existing task."""
        if request.task_id is None:
            return self._error(
                request,
                ProtocolErrorCode.MISSING_REQUIRED_FIELD,
                details={"field": "task_id"},
            )

        task = self._tasks.get(request.task_id)

        if task is None:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_CORRELATION_ID,
                details={"reason": "task does not exist"},
            )

        task_session_id, state_machine = task

        if task_session_id != request.session_id:
            return self._error(
                request,
                ProtocolErrorCode.INVALID_CORRELATION_ID,
                details={"reason": "task does not belong to session"},
            )

        return self._event(
            request,
            EventType.TASK_STATE_CHANGED,
            {
                "task_id": str(request.task_id),
                "session_id": str(request.session_id),
                "state": state_machine.state.value,
            },
            task_id=request.task_id,
        )

    @staticmethod
    def _event(
        request: ClientRequest,
        event_type: EventType,
        payload: dict[str, Any],
        *,
        task_id: UUID | None = None,
    ) -> RuntimeEvent:
        """Create a typed runtime event."""
        return RuntimeEvent(
            protocol_version=PROTOCOL_VERSION,
            event_id=generate_event_id(),
            request_id=request.request_id,
            session_id=request.session_id,
            task_id=task_id if task_id is not None else request.task_id,
            type=event_type,
            payload=payload,
            severity="INFO",
            created_at=datetime.now(UTC),
        )

    @staticmethod
    def _error(
        request: ClientRequest,
        code: ProtocolErrorCode,
        *,
        details: dict[str, Any] | None = None,
    ) -> ProtocolErrorEnvelope:
        """Create a safe typed protocol error."""
        error = ProtocolError(
            code=code,
            message=_CANONICAL_MESSAGES[code],
            request_id=request.request_id,
            details=details or {},
        )

        return ProtocolErrorEnvelope(
            protocol_version=PROTOCOL_VERSION,
            request_id=request.request_id,
            error=error,
            created_at=datetime.now(UTC),
        )
