"""Failure Injection and Error Recovery Validation Suite.

Verifies T110, ADM-018, ADM-T06, and Gate G7/G10 recovery requirements:
- docs/specifications/08 AI_Software_CoAgent_Error_Recovery_Specification_v1.0_FINAL_LOCKED.md
- docs/specifications/09 AI_Software_CoAgent_Testing_Validation_Specification_v1.0_FINAL_LOCKED.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.recovery.budgets import RecoveryBudget, RecoveryBudgetTracker
from coagent.recovery.classifier import ErrorCategory, FailureClassifier
from coagent.recovery.controller import RecoveryController, RecoveryState
from coagent.security.path import WorkspaceEscapeError
from coagent.validation.evidence import GateStatus, ValidationResult
from coagent.validation.runner import ValidationGateDefinition
from coagent.workspace.scope import WorkspaceScope
from tests.fixtures.repo_fixtures import create_broken_build_repo


@pytest.fixture
def recovery_workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "recovery_repo"
    create_broken_build_repo(ws)
    return ws


@pytest.fixture
def scope(recovery_workspace: Path) -> WorkspaceScope:
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(recovery_workspace),
    )


# Test 1: Failure classifier accurately identifies syntax, test failure, and transient tool errors
def test_failure_classifier_categories() -> None:
    classifier = FailureClassifier()

    # Syntax/Execution error classification
    rec_syntax = classifier.classify_exception(SyntaxError("invalid syntax in broken.py line 12"))
    assert rec_syntax.category in (ErrorCategory.EXEC.value, ErrorCategory.SYSTEM.value)

    # Test failure classification
    rec_test = classifier.classify_validation_failure(
        ValidationResult(
            gate_id="test",
            task_id=uuid4(),
            command="pytest",
            status=GateStatus.FAIL,
            stderr_summary="AssertionError: assert 6 == 5",
        )
    )
    assert rec_test.category == ErrorCategory.TEST.value

    # Security exception classification
    rec_sec = classifier.classify_exception(WorkspaceEscapeError("Path traversal attempted"))
    assert rec_sec.category == ErrorCategory.PATH.value
    assert rec_sec.code == "PATH_ESCAPE_ATTEMPT"


# Test 2: Bounded retry budget halts when max attempts are reached
def test_recovery_budget_exhaustion(scope: WorkspaceScope) -> None:
    # Configure strict budget: 2 attempts max
    tracker = RecoveryBudgetTracker(
        budget=RecoveryBudget(max_total_attempts=2, max_consecutive_same_error=5)
    )
    controller = RecoveryController(tracker=tracker)

    failing_gate = ValidationGateDefinition(
        gate_id="persistent_fail",
        command=[sys.executable, "-c", "import sys; sys.exit(1)"],
    )
    failure = ValidationResult(
        gate_id="persistent_fail",
        task_id=scope.task_id,
        command="test",
        status=GateStatus.FAIL,
    )

    # Attempt 1
    o1 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert o1.state == RecoveryState.FAILED

    # Attempt 2
    o2 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert o2.state == RecoveryState.FAILED

    # Attempt 3 -> Exceeded budget!
    o3 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert o3.state == RecoveryState.FAILED
    assert "budget" in (o3.reason or "").lower() or "exhausted" in (o3.reason or "").lower()


# Test 3: Security violations block recovery immediately without retry loops
def test_security_violation_recovery_block(scope: WorkspaceScope) -> None:
    controller = RecoveryController()
    sec_failure = WorkspaceEscapeError("Attempted escape to C:/Windows")

    outcome = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=sec_failure,
    )
    assert outcome.state == RecoveryState.BLOCKED
    assert not outcome.success
    # Does not retry security failures
    assert outcome.attempts == 0


# Test 4: End-to-end recovery of a broken calculation bug
def test_successful_repair_and_retest_e2e(recovery_workspace: Path, scope: WorkspaceScope) -> None:
    calc_file = recovery_workspace / "src" / "broken_calc.py"
    assert "return a * b" in calc_file.read_text(encoding="utf-8")

    # Initial failure
    failure = ValidationResult(
        gate_id="calc_gate",
        task_id=scope.task_id,
        command="pytest",
        status=GateStatus.FAIL,
        stderr_summary="AssertionError: assert 6 == 5",
    )

    # Repair action replaces multiplication with addition
    def repair() -> str:
        calc_file.write_text(
            "def compute(a: int, b: int) -> int:\n    return a + b\n",
            encoding="utf-8",
        )
        return "Fixed operation: changed * to +"

    retest_gate = ValidationGateDefinition(
        gate_id="calc_gate",
        command=[
            sys.executable,
            "-c",
            "from src.broken_calc import compute; assert compute(2, 3) == 5",
        ],
    )

    controller = RecoveryController()
    outcome = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        repair_action=repair,
        retest_gates=[retest_gate],
    )

    assert outcome.success is True
    assert outcome.state == RecoveryState.RECOVERED
    assert outcome.retest_results[0].status == GateStatus.PASS
