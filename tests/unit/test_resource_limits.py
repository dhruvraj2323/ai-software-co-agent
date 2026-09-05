"""Unit tests for T025 resource, time, and concurrency limits."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from coagent.security import (
    ResourceLimiter,
    ResourceLimitExceededError,
    ResourceLimits,
)


def make_limits() -> ResourceLimits:
    """Create explicit deterministic test limits."""
    return ResourceLimits(
        max_execution_seconds=10,
        max_concurrent_operations=2,
        max_tool_calls=2,
        max_recovery_attempts=2,
        max_output_bytes=100,
    )


def test_resource_limits_require_positive_values() -> None:
    """Security limits reject zero or negative values."""
    with pytest.raises(ValidationError):
        ResourceLimits(
            max_execution_seconds=0,
            max_concurrent_operations=1,
            max_tool_calls=1,
            max_recovery_attempts=1,
            max_output_bytes=1,
        )


def test_resource_limits_reject_unknown_fields() -> None:
    """Limit configuration does not silently accept unknown settings."""
    with pytest.raises(ValidationError):
        ResourceLimits(
            max_execution_seconds=1,
            max_concurrent_operations=1,
            max_tool_calls=1,
            max_recovery_attempts=1,
            max_output_bytes=1,
            unexpected=1,
        )


def test_execution_time_is_enforced() -> None:
    """Execution exceeding its configured time budget is blocked."""
    now = [100.0]
    limiter = ResourceLimiter(make_limits(), clock=lambda: now[0])
    limiter.start_execution()
    now[0] = 110.1
    with pytest.raises(ResourceLimitExceededError):
        limiter.check_execution_time()


def test_execution_within_time_limit_is_allowed() -> None:
    """Execution within its configured time budget remains allowed."""
    now = [100.0]
    limiter = ResourceLimiter(make_limits(), clock=lambda: now[0])
    limiter.start_execution()
    now[0] = 109.0
    limiter.check_execution_time()


def test_concurrent_operations_are_bounded() -> None:
    """Concurrent operations cannot exceed the configured limit."""
    limiter = ResourceLimiter(make_limits())
    limiter.acquire_operation()
    limiter.acquire_operation()
    with pytest.raises(ResourceLimitExceededError):
        limiter.acquire_operation()
    assert limiter.active_operations == 2


def test_releasing_operation_restores_capacity() -> None:
    """Released concurrency capacity can be reused."""
    limiter = ResourceLimiter(make_limits())
    limiter.acquire_operation()
    limiter.acquire_operation()
    limiter.release_operation()
    limiter.acquire_operation()
    assert limiter.active_operations == 2


def test_tool_calls_are_bounded() -> None:
    """Tool-call consumption stops at the configured budget."""
    limiter = ResourceLimiter(make_limits())
    limiter.consume_tool_call()
    limiter.consume_tool_call()
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_tool_call()
    assert limiter.tool_calls == 2


def test_recovery_attempts_are_bounded() -> None:
    """Recovery attempts stop at the configured budget."""
    limiter = ResourceLimiter(make_limits())
    limiter.consume_recovery_attempt()
    limiter.consume_recovery_attempt()
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_recovery_attempt()
    assert limiter.recovery_attempts == 2


def test_output_bytes_are_bounded() -> None:
    """Output capture cannot exceed the configured byte budget."""
    limiter = ResourceLimiter(make_limits())
    limiter.consume_output_bytes(40)
    limiter.consume_output_bytes(60)
    with pytest.raises(ResourceLimitExceededError):
        limiter.consume_output_bytes(1)
    assert limiter.output_bytes == 100


def test_negative_output_consumption_is_rejected() -> None:
    """Negative output consumption cannot corrupt the budget."""
    limiter = ResourceLimiter(make_limits())
    with pytest.raises(ValueError):
        limiter.consume_output_bytes(-1)


def test_execution_cannot_be_started_twice() -> None:
    """An active execution window cannot be silently replaced."""
    limiter = ResourceLimiter(make_limits())
    limiter.start_execution()
    with pytest.raises(ResourceLimitExceededError):
        limiter.start_execution()


def test_execution_can_be_stopped_and_started_again() -> None:
    """Stopping execution releases the execution-window state."""
    limiter = ResourceLimiter(make_limits())
    limiter.start_execution()
    limiter.stop_execution()
    limiter.start_execution()
    limiter.check_execution_time()
