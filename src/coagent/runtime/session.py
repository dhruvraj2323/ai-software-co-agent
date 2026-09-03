"""Runtime-owned session state and lifecycle management."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from coagent.core.ids import generate_session_id


class SessionState(StrEnum):
    """Lifecycle states for a runtime-owned session."""

    ACTIVE = "ACTIVE"
    DISCONNECTED = "DISCONNECTED"
    TERMINATED = "TERMINATED"


class InvalidSessionTransitionError(ValueError):
    """Raised when a session lifecycle transition is not permitted."""


class Session:
    """Runtime-owned session with centralized lifecycle transitions."""

    def __init__(
        self,
        session_id: UUID | None = None,
        *,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        now = datetime.now(UTC)
        self.session_id = session_id or generate_session_id()
        self.state = SessionState.ACTIVE
        self.created_at = created_at or now
        self.updated_at = updated_at or self.created_at

    def transition(self, target: SessionState) -> None:
        """Transition the session to an allowed lifecycle state."""
        allowed = {
            SessionState.ACTIVE: {
                SessionState.DISCONNECTED,
                SessionState.TERMINATED,
            },
            SessionState.DISCONNECTED: {
                SessionState.ACTIVE,
                SessionState.TERMINATED,
            },
            SessionState.TERMINATED: set(),
        }

        if target not in allowed[self.state]:
            raise InvalidSessionTransitionError(
                f"invalid session transition: {self.state} -> {target}"
            )

        self.state = target
        self.updated_at = datetime.now(UTC)

    def disconnect(self) -> None:
        """Record client disconnection without terminating the runtime session."""
        self.transition(SessionState.DISCONNECTED)

    def reconnect(self) -> None:
        """Reattach a disconnected session without changing its identity."""
        self.transition(SessionState.ACTIVE)

    def terminate(self) -> None:
        """Terminate the session permanently."""
        self.transition(SessionState.TERMINATED)
