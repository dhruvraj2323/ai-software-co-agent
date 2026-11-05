"""Execution-layer resource limits and budget controls (T042, T048)."""

from __future__ import annotations

from coagent.security.limits import (
    ResourceLimiter,
    ResourceLimitExceededError,
    ResourceLimits,
)

DEFAULT_PROCESS_TIMEOUT_SECONDS: float = 30.0
DEFAULT_MAX_OUTPUT_BYTES: int = 1_000_000  # 1 MB maximum output buffer
DEFAULT_MAX_FILE_BYTES: int = 10_000_000  # 10 MB maximum file read/write

__all__ = [
    "DEFAULT_MAX_FILE_BYTES",
    "DEFAULT_MAX_OUTPUT_BYTES",
    "DEFAULT_PROCESS_TIMEOUT_SECONDS",
    "ResourceLimitExceededError",
    "ResourceLimiter",
    "ResourceLimits",
]
