"""Runtime-owned task lifecycle state machine."""

from __future__ import annotations

from enum import StrEnum


class TaskState(StrEnum):
    """Canonical runtime task lifecycle states."""

    CREATED = "CREATED"
    PLANNING = "PLANNING"
    READY = "READY"
    IMPLEMENTING = "IMPLEMENTING"
    VALIDATING = "VALIDATING"
    RECOVERING = "RECOVERING"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"


class InvalidTaskTransitionError(ValueError):
    """Raised when a task lifecycle transition is not permitted."""


class TaskStateMachine:
    """Validate and apply canonical task lifecycle transitions."""

    _ALLOWED_TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
        TaskState.CREATED: frozenset(
            {
                TaskState.PLANNING,
                TaskState.CANCELLED,
            }
        ),
        TaskState.PLANNING: frozenset(
            {
                TaskState.READY,
                TaskState.BLOCKED,
                TaskState.FAILED,
                TaskState.CANCELLED,
            }
        ),
        TaskState.READY: frozenset(
            {
                TaskState.IMPLEMENTING,
                TaskState.BLOCKED,
                TaskState.CANCELLED,
            }
        ),
        TaskState.IMPLEMENTING: frozenset(
            {
                TaskState.VALIDATING,
                TaskState.BLOCKED,
                TaskState.FAILED,
                TaskState.CANCELLED,
            }
        ),
        TaskState.VALIDATING: frozenset(
            {
                TaskState.COMPLETE,
                TaskState.RECOVERING,
                TaskState.FAILED,
                TaskState.BLOCKED,
                TaskState.CANCELLED,
            }
        ),
        TaskState.RECOVERING: frozenset(
            {
                TaskState.VALIDATING,
                TaskState.BLOCKED,
                TaskState.FAILED,
                TaskState.CANCELLED,
            }
        ),
        TaskState.BLOCKED: frozenset(
            {
                TaskState.READY,
                TaskState.IMPLEMENTING,
                TaskState.CANCELLED,
            }
        ),
        TaskState.FAILED: frozenset(),
        TaskState.COMPLETE: frozenset(),
        TaskState.CANCELLED: frozenset(),
    }

    def __init__(self, initial_state: TaskState = TaskState.CREATED) -> None:
        self.state = initial_state

    def can_transition(
        self,
        target: TaskState,
        *,
        recovery_available: bool = False,
    ) -> bool:
        """Return whether a requested transition is permitted."""
        if target is TaskState.RECOVERING:
            return target in self._ALLOWED_TRANSITIONS[self.state] and recovery_available

        return target in self._ALLOWED_TRANSITIONS[self.state]

    def transition(
        self,
        target: TaskState,
        *,
        recovery_available: bool = False,
    ) -> None:
        """Apply a permitted lifecycle transition."""
        if not self.can_transition(
            target,
            recovery_available=recovery_available,
        ):
            raise InvalidTaskTransitionError(f"invalid task transition: {self.state} -> {target}")

        self.state = target
