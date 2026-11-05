"""Cancellation primitives for execution tasks (T046)."""

from __future__ import annotations

import threading


class CancellationToken:
    """Thread-safe cancellation token passed to long-running executors."""

    def __init__(self) -> None:
        self._is_cancelled = threading.Event()
        self._reason: str | None = None

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._is_cancelled.is_set()

    @property
    def reason(self) -> str | None:
        """Return the reason for cancellation, if provided."""
        return self._reason

    def cancel(self, reason: str = "Execution cancelled by caller.") -> None:
        """Signal cancellation with an optional reason."""
        self._reason = reason
        self._is_cancelled.set()

    def check(self) -> None:
        """Raise an OperationCancelledError if cancellation was requested."""
        if self._is_cancelled.is_set():
            raise OperationCancelledError(self._reason or "Operation cancelled.")


class OperationCancelledError(RuntimeError):
    """Raised when an operation is aborted due to cancellation."""
