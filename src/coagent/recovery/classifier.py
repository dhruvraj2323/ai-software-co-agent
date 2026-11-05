"""Failure classification and canonical ErrorRecord mapping (ERS-001 §5, §6)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.execution.patch import PatchConflictError
from coagent.git.adapter import GitExecutionError
from coagent.security.path import WorkspaceEscapeError
from coagent.validation.evidence import ValidationResult


class ErrorCategory(StrEnum):
    """Canonical error category taxonomy (ERS-001 §5)."""

    TASK = "TASK"
    CTX = "CTX"
    LLM = "LLM"
    TOOL = "TOOL"
    POL = "POL"
    PATH = "PATH"
    EXEC = "EXEC"
    PATCH = "PATCH"
    TEST = "TEST"
    GIT = "GIT"
    MCP = "MCP"
    PERSIST = "PERSIST"
    SYSTEM = "SYSTEM"


class FailureClassifier:
    """Classifies raw errors, exceptions, and validation failures into bounded categories."""

    def classify_validation_failure(
        self,
        result: ValidationResult,
    ) -> ErrorRecord:
        """Classify a non-passing ValidationResult into an ErrorRecord."""
        now = datetime.now(UTC)
        err_msg = (
            result.stderr_summary or result.stdout_summary or f"Gate '{result.gate_id}' failed"
        )

        return ErrorRecord(
            error_id=uuid4(),
            task_id=result.task_id,
            correlation_id=uuid4(),
            category=ErrorCategory.TEST.value,
            code=f"VAL-{result.status.value}",
            source=f"gate:{result.gate_id}",
            message=err_msg,
            severity=EventSeverity.ERROR,
            recoverability=Recoverability.AUTO,
            evidence_refs=[f"evidence://validation/{result.result_id}"],
            retry_key=f"val_{result.gate_id}",
            occurred_at=result.captured_at,
            normalized_at=now,
        )

    def classify_exception(
        self,
        exc: Exception,
        task_id: UUID | None = None,
        source: str = "runtime",
    ) -> ErrorRecord:
        """Classify an unexpected exception into a structured ErrorRecord."""
        now = datetime.now(UTC)
        msg = str(exc)

        # 1. Path traversal and boundary security violations
        if isinstance(exc, WorkspaceEscapeError):
            return ErrorRecord(
                error_id=uuid4(),
                task_id=task_id,
                correlation_id=uuid4(),
                category=ErrorCategory.PATH.value,
                code="PATH_ESCAPE_ATTEMPT",
                source=source,
                message=msg,
                severity=EventSeverity.CRITICAL,
                recoverability=Recoverability.MANUAL,  # Never auto-bypass security boundaries
                retry_key=None,
                occurred_at=now,
                normalized_at=now,
            )

        # 2. Patch and editing conflicts
        if isinstance(exc, PatchConflictError):
            return ErrorRecord(
                error_id=uuid4(),
                task_id=task_id,
                correlation_id=uuid4(),
                category=ErrorCategory.PATCH.value,
                code="PATCH_CONFLICT",
                source=source,
                message=msg,
                severity=EventSeverity.ERROR,
                recoverability=Recoverability.AUTO,
                retry_key="patch_conflict",
                occurred_at=now,
                normalized_at=now,
            )

        # 3. Git execution failures
        if isinstance(exc, GitExecutionError):
            return ErrorRecord(
                error_id=uuid4(),
                task_id=task_id,
                correlation_id=uuid4(),
                category=ErrorCategory.GIT.value,
                code="GIT_ERROR",
                source=source,
                message=msg,
                severity=EventSeverity.ERROR,
                recoverability=Recoverability.ASSISTED,
                retry_key="git_error",
                occurred_at=now,
                normalized_at=now,
            )

        # 4. Timeout exceptions
        if isinstance(exc, TimeoutError):
            return ErrorRecord(
                error_id=uuid4(),
                task_id=task_id,
                correlation_id=uuid4(),
                category=ErrorCategory.EXEC.value,
                code="EXECUTION_TIMEOUT",
                source=source,
                message=msg,
                severity=EventSeverity.WARNING,
                recoverability=Recoverability.AUTO,
                retry_key="timeout",
                occurred_at=now,
                normalized_at=now,
            )

        # 5. Default generic error
        return ErrorRecord(
            error_id=uuid4(),
            task_id=task_id,
            correlation_id=uuid4(),
            category=ErrorCategory.SYSTEM.value,
            code="UNHANDLED_EXCEPTION",
            source=source,
            message=msg,
            severity=EventSeverity.ERROR,
            recoverability=Recoverability.MANUAL,
            retry_key="general_error",
            occurred_at=now,
            normalized_at=now,
        )
