"""Unit tests for RecoveryController, budgets, and retry loops (T080, T081, T082, T084)."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

from coagent.recovery.budgets import RecoveryBudget, RecoveryBudgetTracker
from coagent.recovery.controller import RecoveryController, RecoveryState
from coagent.security.path import WorkspaceEscapeError
from coagent.validation.evidence import GateStatus, ValidationResult
from coagent.validation.runner import ValidationGateDefinition
from coagent.workspace.scope import WorkspaceScope


def test_recovery_controller_successful_repair_and_retest(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    target_file = workspace_dir / "calc.py"
    target_file.write_text("def add(a, b): return a - b\n", encoding="utf-8")  # Bug!

    # Failing validation result
    failure = ValidationResult(
        gate_id="calc_test",
        task_id=scope.task_id,
        command="pytest",
        status=GateStatus.FAIL,
        stderr_summary="AssertionError: 2 != 0",
    )

    # Repair action: fix the bug
    def fix_bug():
        target_file.write_text("def add(a, b): return a + b\n", encoding="utf-8")
        return "Fixed addition operator"

    # Retest gate: runs python check
    retest_gate = ValidationGateDefinition(
        gate_id="calc_test",
        command=[
            sys.executable,
            "-c",
            "from calc import add; assert add(1, 1) == 2",
        ],
    )

    controller = RecoveryController()
    outcome = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        repair_action=fix_bug,
        retest_gates=[retest_gate],
    )

    assert outcome.state == RecoveryState.RECOVERED
    assert outcome.success is True
    assert outcome.attempts == 1
    assert "Fixed addition operator" in str(outcome.repair_description)
    assert len(outcome.retest_results) == 1
    assert outcome.retest_results[0].status == GateStatus.PASS


def test_recovery_controller_blocks_security_violations(tmp_path: Path) -> None:
    """Security violations (e.g. WorkspaceEscapeError) must NOT be auto-repaired."""
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))

    controller = RecoveryController()
    escape_exc = WorkspaceEscapeError("Attempted path traversal to /etc/shadow")

    outcome = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=escape_exc,
    )

    assert outcome.state == RecoveryState.BLOCKED
    assert outcome.success is False
    assert "requires human intervention" in (outcome.reason or "")


def test_recovery_controller_loop_detection(tmp_path: Path) -> None:
    """Consecutive same errors must trigger loop detection and halt."""
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))

    tracker = RecoveryBudgetTracker(
        budget=RecoveryBudget(max_total_attempts=5, max_consecutive_same_error=2)
    )
    controller = RecoveryController(tracker=tracker)

    failure = ValidationResult(
        gate_id="broken_gate",
        task_id=scope.task_id,
        command="pytest",
        status=GateStatus.FAIL,
    )

    failing_gate = ValidationGateDefinition(
        gate_id="broken_gate",
        command=[sys.executable, "-c", "import sys; sys.exit(1)"],
    )

    # Attempt 1 -> fails retest
    outcome1 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert outcome1.state == RecoveryState.FAILED

    # Attempt 2 -> fails retest
    outcome2 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert outcome2.state == RecoveryState.FAILED

    # Attempt 3 -> Loop detected! (exceeded max_consecutive_same_error=2)
    outcome3 = controller.attempt_recovery(
        task_id=scope.task_id,
        scope=scope,
        failure=failure,
        retest_gates=[failing_gate],
    )
    assert outcome3.state == RecoveryState.FAILED
    assert "loop detected" in (outcome3.reason or "").lower()
