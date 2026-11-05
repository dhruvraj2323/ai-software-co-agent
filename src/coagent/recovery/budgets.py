"""Recovery budgets, attempt tracking, and loop prevention (ERS-001 §8, §15)."""

from __future__ import annotations

import time

from pydantic import BaseModel, ConfigDict, Field


class RecoveryBudget(BaseModel):
    """Resource constraints bounding error recovery loops."""

    model_config = ConfigDict(extra="forbid")

    max_total_attempts: int = Field(default=3, ge=1)
    max_consecutive_same_error: int = Field(default=2, ge=1)
    timeout_seconds: float = Field(default=300.0, ge=1.0)


class RecoveryBudgetTracker:
    """Tracks recovery attempts and prevents infinite recovery loops."""

    def __init__(self, budget: RecoveryBudget | None = None) -> None:
        self.budget = budget or RecoveryBudget()
        self.attempts: int = 0
        self._key_attempts: dict[str, int] = {}
        self._last_key: str | None = None
        self._consecutive_same_key: int = 0
        self._start_time: float = time.perf_counter()

    @property
    def is_exhausted(self) -> bool:
        """Return True if attempts limit or elapsed time exceeds configured budget."""
        if self.attempts >= self.budget.max_total_attempts:
            return True
        elapsed = time.perf_counter() - self._start_time
        return elapsed > self.budget.timeout_seconds

    def is_loop_detected(self, retry_key: str | None) -> bool:
        """Return True if the same error is repeatedly triggering recovery without progress."""
        if not retry_key:
            return False
        max_same = self.budget.max_consecutive_same_error
        if retry_key == self._last_key and self._consecutive_same_key >= max_same:
            return True
        return False

    def record_attempt(self, retry_key: str | None) -> None:
        """Record a recovery attempt for a given failure key."""
        self.attempts += 1
        key = retry_key or "unknown"
        self._key_attempts[key] = self._key_attempts.get(key, 0) + 1

        if key == self._last_key:
            self._consecutive_same_key += 1
        else:
            self._last_key = key
            self._consecutive_same_key = 1
