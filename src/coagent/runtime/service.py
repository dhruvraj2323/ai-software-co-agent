"""Runtime service for safe session, task, and client protocol commands (T019, T095)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from coagent.core.ids import generate_event_id, generate_task_id
from coagent.core.types import EventSeverity
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
    """In-process runtime command service dispatching typed protocol messages.

    T019 and T095: Exposes safe session, task, plan, and diagnostic operations
    strictly through the versioned client protocol.
    """

    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}
        self._tasks: dict[UUID, tuple[UUID, TaskStateMachine]] = {}
        self._task_data: dict[UUID, dict[str, Any]] = {}

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

        if request.type is RequestType.PLAN_REQUEST:
            return self._handle_plan_request(request)

        if request.type is RequestType.TASK_CANCEL:
            return self._handle_task_cancel(request)

        if request.type is RequestType.APPROVAL_RESPOND:
            return self._handle_approval_respond(request)

        if request.type is RequestType.DIFF_OPEN:
            return self._handle_diff_open(request)

        if request.type is RequestType.COMPLETION_STATUS:
            return self._handle_completion_status(request)

        if request.type is RequestType.WORKSPACE_REFRESH:
            return self._handle_workspace_refresh(request)

        if request.type is RequestType.ARTIFACT_OPEN:
            return self._handle_artifact_open(request)

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
        self._task_data[task_id] = {
            "goal": request.payload.get("goal", ""),
            "files": request.payload.get("files", []),
            "plan": [],
            "diff": "",
        }

        return self._event(
            request,
            EventType.TASK_CREATED,
            {
                "task_id": str(task_id),
                "session_id": str(request.session_id),
                "state": TaskState.CREATED.value,
                "goal": self._task_data[task_id]["goal"],
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

    def _handle_plan_request(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Generate and update plan for an existing task."""
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

        # Transition task to READY via PLANNING if possible
        if state_machine.can_transition(TaskState.PLANNING):
            state_machine.transition(TaskState.PLANNING)
        if state_machine.can_transition(TaskState.READY):
            state_machine.transition(TaskState.READY)

        goal = self._task_data.get(request.task_id, {}).get("goal", "Execute engineering task")
        steps = [
            {"step": 1, "description": f"Analyze requirement: {goal}"},
            {"step": 2, "description": "Execute authorized code modification"},
            {"step": 3, "description": "Run validation gates and verify completion"},
        ]
        self._task_data[request.task_id]["plan"] = steps

        return self._event(
            request,
            EventType.PLAN_UPDATED,
            {
                "task_id": str(request.task_id),
                "session_id": str(request.session_id),
                "state": state_machine.state.value,
                "plan": steps,
            },
            task_id=request.task_id,
        )

    def _handle_task_cancel(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Cancel an in-progress or pending task."""
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

        reason = request.payload.get("reason", "Cancelled by client request")
        if state_machine.can_transition(TaskState.CANCELLED):
            state_machine.transition(TaskState.CANCELLED)

        return self._event(
            request,
            EventType.TASK_CANCELLED,
            {
                "task_id": str(request.task_id),
                "session_id": str(request.session_id),
                "state": state_machine.state.value,
                "reason": reason,
            },
            task_id=request.task_id,
        )

    def _handle_approval_respond(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Record an explicit user approval response for an action."""
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

        approved = bool(request.payload.get("approved", False))
        approval_id = request.payload.get("approval_id", "")
        reason = request.payload.get("reason", "")

        # If approved and task was blocked, transition to READY
        if approved and state_machine.state is TaskState.BLOCKED:
            if state_machine.can_transition(TaskState.READY):
                state_machine.transition(TaskState.READY)

        return self._event(
            request,
            EventType.TASK_STATE_CHANGED,
            {
                "task_id": str(request.task_id),
                "approval_id": approval_id,
                "approved": approved,
                "reason": reason,
                "state": state_machine.state.value,
            },
            task_id=request.task_id,
        )

    def _handle_diff_open(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Return the current task diff/patch summary."""
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

        diff_content = self._task_data.get(request.task_id, {}).get("diff", "")
        return self._event(
            request,
            EventType.CONTEXT_UPDATED,
            {
                "task_id": str(request.task_id),
                "diff": diff_content,
            },
            task_id=request.task_id,
        )

    def _handle_completion_status(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Return the task completion evaluation."""
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

        _, state_machine = task
        is_complete = state_machine.state is TaskState.COMPLETE
        event_type = EventType.TASK_COMPLETED if is_complete else EventType.TASK_STATE_CHANGED

        return self._event(
            request,
            event_type,
            {
                "task_id": str(request.task_id),
                "state": state_machine.state.value,
                "is_complete": is_complete,
            },
            task_id=request.task_id,
        )

    def _handle_workspace_refresh(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent:
        """Handle workspace scope/context refresh."""
        return self._event(
            request,
            EventType.CONTEXT_UPDATED,
            {
                "session_id": str(request.session_id),
                "status": "workspace_refreshed",
            },
        )

    def _handle_artifact_open(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent:
        """Handle opening a safe artifact reference."""
        artifact_id = request.payload.get("artifact_id", "")
        return self._event(
            request,
            EventType.CONTEXT_UPDATED,
            {
                "artifact_id": artifact_id,
                "status": "ready",
            },
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
            severity=EventSeverity.INFO,
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
