"""Protocol-based runtime client for the CLI interface (T095, REQ-095)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from coagent.protocol.errors import ProtocolErrorEnvelope
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    RequestType,
    RuntimeEvent,
)
from coagent.runtime.service import RuntimeService


class RuntimeClientError(RuntimeError):
    """Raised when the runtime returns an error envelope."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"Runtime error [{code}]: {message}")
        self.code = code
        self.message = message
        self.details = details or {}


class RuntimeClient:
    """Headless/CLI client interacting with the Co-Agent runtime strictly via protocol envelopes."""

    def __init__(
        self,
        service: RuntimeService | None = None,
        session_id: UUID | None = None,
    ) -> None:
        self._service = service or RuntimeService()
        self.session_id: UUID = session_id or uuid4()
        self.current_task_id: UUID | None = None
        self._session_started: bool = False

    def ensure_session(self) -> RuntimeEvent:
        """Ensure an active runtime session exists."""
        if self._session_started:
            req = self._make_request(RequestType.SESSION_START)
            return self._execute(req)

        req = self._make_request(RequestType.SESSION_START)
        event = self._execute(req)
        self._session_started = True
        return event

    def create_task(
        self,
        goal: str,
        files: list[str] | None = None,
        task_id: UUID | None = None,
    ) -> RuntimeEvent:
        """Request creation of a new task in the active session."""
        self.ensure_session()
        actual_task_id = task_id or uuid4()
        req = self._make_request(
            RequestType.TASK_CREATE,
            task_id=actual_task_id,
            payload={"goal": goal, "files": files or []},
        )
        event = self._execute(req)
        self.current_task_id = actual_task_id
        return event

    def get_status(self, task_id: UUID | None = None) -> RuntimeEvent:
        """Fetch current status for a given task."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(RequestType.TASK_STATUS, task_id=target)
        return self._execute(req)

    def request_plan(self, task_id: UUID | None = None) -> RuntimeEvent:
        """Request plan generation for an existing task."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(RequestType.PLAN_REQUEST, task_id=target)
        return self._execute(req)

    def respond_approval(
        self,
        approval_id: str,
        approved: bool,
        task_id: UUID | None = None,
        reason: str | None = None,
    ) -> RuntimeEvent:
        """Submit a user approval response to the runtime."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(
            RequestType.APPROVAL_RESPOND,
            task_id=target,
            payload={
                "approval_id": approval_id,
                "approved": approved,
                "reason": reason or "",
            },
        )
        return self._execute(req)

    def cancel_task(
        self,
        task_id: UUID | None = None,
        reason: str | None = None,
    ) -> RuntimeEvent:
        """Request cancellation of an in-progress or queued task."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(
            RequestType.TASK_CANCEL,
            task_id=target,
            payload={"reason": reason or "Cancelled by user via CLI"},
        )
        return self._execute(req)

    def get_diff(self, task_id: UUID | None = None) -> RuntimeEvent:
        """Request task-level diff/patch inspection."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(RequestType.DIFF_OPEN, task_id=target)
        return self._execute(req)

    def get_completion_status(self, task_id: UUID | None = None) -> RuntimeEvent:
        """Query task completion validation status."""
        self.ensure_session()
        target = task_id or self.current_task_id
        if target is None:
            raise ValueError("No active task_id provided.")

        req = self._make_request(RequestType.COMPLETION_STATUS, task_id=target)
        return self._execute(req)

    def refresh_workspace(self) -> RuntimeEvent:
        """Request workspace scope and context refresh."""
        self.ensure_session()
        req = self._make_request(RequestType.WORKSPACE_REFRESH)
        return self._execute(req)

    def open_artifact(self, artifact_id: str, task_id: UUID | None = None) -> RuntimeEvent:
        """Request safe access to an offloaded artifact."""
        self.ensure_session()
        req = self._make_request(
            RequestType.ARTIFACT_OPEN,
            task_id=task_id or self.current_task_id,
            payload={"artifact_id": artifact_id},
        )
        return self._execute(req)

    def send_raw_request(
        self,
        request: ClientRequest,
    ) -> RuntimeEvent | ProtocolErrorEnvelope:
        """Directly dispatch a ClientRequest to the runtime (for protocol testing)."""
        return self._service.handle(request)

    def _make_request(
        self,
        req_type: RequestType,
        task_id: UUID | None = None,
        payload: dict[str, Any] | None = None,
        client_context: dict[str, Any] | None = None,
    ) -> ClientRequest:
        """Factory helper creating versioned ClientRequest envelopes."""
        return ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=self.session_id,
            task_id=task_id,
            type=req_type,
            payload=payload or {},
            client_context=client_context or {"client": "coagent-cli", "version": "0.1.0"},
            created_at=datetime.now(UTC),
        )

    def _execute(self, request: ClientRequest) -> RuntimeEvent:
        """Deliver request to runtime and return event, raising on protocol error."""
        result = self._service.handle(request)
        if isinstance(result, ProtocolErrorEnvelope):
            raise RuntimeClientError(
                code=result.error.code.value,
                message=result.error.message,
                details=result.error.details,
            )
        return result
