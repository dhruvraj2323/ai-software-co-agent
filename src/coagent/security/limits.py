"""Resource, time, and concurrency limit enforcement primitives."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic

from pydantic import BaseModel, ConfigDict, Field


class ResourceLimitExceededError(RuntimeError):
    """Raised when a configured resource limit would be exceeded."""


class ResourceLimits(BaseModel):
    """Explicit limits for bounded task/resource consumption."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    max_execution_seconds: float = Field(gt=0)
    max_concurrent_operations: int = Field(gt=0)
    max_tool_calls: int = Field(gt=0)
    max_recovery_attempts: int = Field(gt=0)
    max_output_bytes: int = Field(gt=0)


@dataclass
class ResourceLimiter:
    """Track and enforce configured execution/resource budgets."""

    limits: ResourceLimits
    clock: Callable[[], float] = monotonic
    _execution_started_at: float | None = None
    _active_operations: int = 0
    _tool_calls: int = 0
    _recovery_attempts: int = 0
    _output_bytes: int = 0

    def start_execution(self) -> None:
        """Start a bounded execution window."""
        if self._execution_started_at is not None:
            raise ResourceLimitExceededError("execution is already active")
        self._execution_started_at = self.clock()

    def stop_execution(self) -> None:
        """Stop the active execution window."""
        self._execution_started_at = None

    def check_execution_time(self) -> None:
        """Raise if the active execution window exceeded its time budget."""
        if self._execution_started_at is None:
            return
        elapsed = self.clock() - self._execution_started_at
        if elapsed > self.limits.max_execution_seconds:
            raise ResourceLimitExceededError("execution time limit exceeded")

    def acquire_operation(self) -> None:
        """Acquire one concurrent-operation slot."""
        if self._active_operations >= self.limits.max_concurrent_operations:
            raise ResourceLimitExceededError("concurrent operation limit exceeded")
        self._active_operations += 1

    def release_operation(self) -> None:
        """Release one concurrent-operation slot."""
        if self._active_operations > 0:
            self._active_operations -= 1

    def consume_tool_call(self) -> None:
        """Consume one tool-call budget unit."""
        if self._tool_calls >= self.limits.max_tool_calls:
            raise ResourceLimitExceededError("tool call limit exceeded")
        self._tool_calls += 1

    def consume_recovery_attempt(self) -> None:
        """Consume one recovery-attempt budget unit."""
        if self._recovery_attempts >= self.limits.max_recovery_attempts:
            raise ResourceLimitExceededError("recovery attempt limit exceeded")
        self._recovery_attempts += 1

    def consume_output_bytes(self, amount: int) -> None:
        """Consume output-byte budget."""
        if amount < 0:
            raise ValueError("output byte amount must be non-negative")
        if self._output_bytes + amount > self.limits.max_output_bytes:
            raise ResourceLimitExceededError("output byte limit exceeded")
        self._output_bytes += amount

    @property
    def active_operations(self) -> int:
        """Return the current concurrent-operation count."""
        return self._active_operations

    @property
    def tool_calls(self) -> int:
        """Return the number of consumed tool-call units."""
        return self._tool_calls

    @property
    def recovery_attempts(self) -> int:
        """Return the number of consumed recovery-attempt units."""
        return self._recovery_attempts

    @property
    def output_bytes(self) -> int:
        """Return the number of consumed output bytes."""
        return self._output_bytes
