"""Unit tests for FailureClassifier (T079)."""

from __future__ import annotations

from uuid import uuid4

from coagent.core.types import EventSeverity, Recoverability
from coagent.execution.patch import PatchConflictError
from coagent.recovery.classifier import ErrorCategory, FailureClassifier
from coagent.security.path import WorkspaceEscapeError
from coagent.validation.evidence import GateStatus, ValidationResult


def test_classify_validation_failure() -> None:
    classifier = FailureClassifier()
    result = ValidationResult(
        gate_id="unit_test",
        task_id=uuid4(),
        command="pytest",
        status=GateStatus.FAIL,
        stderr_summary="AssertionError in test_app.py",
    )

    record = classifier.classify_validation_failure(result)
    assert record.category == ErrorCategory.TEST.value
    assert record.code == "VAL-FAIL"
    assert record.recoverability == Recoverability.AUTO
    assert "AssertionError" in record.message


def test_classify_security_escape_exception() -> None:
    classifier = FailureClassifier()
    exc = WorkspaceEscapeError("Path traversal escape detected: ../secret.txt")

    record = classifier.classify_exception(exc)
    assert record.category == ErrorCategory.PATH.value
    assert record.code == "PATH_ESCAPE_ATTEMPT"
    assert record.severity == EventSeverity.CRITICAL
    assert record.recoverability == Recoverability.MANUAL  # Security escapes are not auto-bypassed


def test_classify_patch_conflict_exception() -> None:
    classifier = FailureClassifier()
    exc = PatchConflictError(
        code="PATCH_CONFLICT",
        message="Hunk 1 failed: file has conflicting local modifications",
    )

    record = classifier.classify_exception(exc)
    assert record.category == ErrorCategory.PATCH.value
    assert record.code == "PATCH_CONFLICT"
    assert record.recoverability == Recoverability.AUTO
