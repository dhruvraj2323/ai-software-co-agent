"""Execution engine: scoped filesystem, bounded processes, and patch management."""

from __future__ import annotations

from coagent.execution.cancellation import (
    CancellationToken,
    OperationCancelledError,
)
from coagent.execution.filesystem import FilesystemExecutor
from coagent.execution.limits import (
    DEFAULT_MAX_FILE_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_PROCESS_TIMEOUT_SECONDS,
    ResourceLimiter,
    ResourceLimitExceededError,
    ResourceLimits,
)
from coagent.execution.patch import (
    FilePatch,
    Patch,
    PatchApplyResult,
    PatchConflictError,
    PatchEngine,
    PatchOperationType,
    compute_file_hash,
)
from coagent.execution.process import (
    ProcessExecutor,
    sanitize_process_environment,
)

__all__ = [
    "CancellationToken",
    "DEFAULT_MAX_FILE_BYTES",
    "DEFAULT_MAX_OUTPUT_BYTES",
    "DEFAULT_PROCESS_TIMEOUT_SECONDS",
    "FilePatch",
    "FilesystemExecutor",
    "OperationCancelledError",
    "Patch",
    "PatchApplyResult",
    "PatchConflictError",
    "PatchEngine",
    "PatchOperationType",
    "ProcessExecutor",
    "ResourceLimitExceededError",
    "ResourceLimiter",
    "ResourceLimits",
    "compute_file_hash",
    "sanitize_process_environment",
]
