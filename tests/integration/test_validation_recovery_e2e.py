"""End-to-end integration tests for Validation, Error Recovery, and Completion Gate (T085)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from uuid import uuid4

from coagent.recovery.controller import RecoveryController, RecoveryState
from coagent.validation.completion import CompletionGate
from coagent.validation.evidence import GateCategory, GateStatus
from coagent.validation.runner import ValidationGateDefinition, ValidationRunner
from coagent.workspace.scope import WorkspaceScope


def test_validation_recovery_and_completion_e2e(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(workspace_dir))

    # 1. Initial implementation with an arithmetic bug
    calc_file = workspace_dir / "calculator.py"
    calc_file.write_text(
        "def multiply(a, b):\n    return a + b  # Bug: addition instead of multiplication\n",
        encoding="utf-8",
    )

    test_file = workspace_dir / "test_calculator.py"
    test_file.write_text(
        "from calculator import multiply\n"
        "def test_mult():\n"
        "    assert multiply(3, 4) == 12\n",
        encoding="utf-8",
    )

    # 2. Setup Validation Gate
    gate_def = ValidationGateDefinition(
        gate_id="unit_mult_test",
        command=[sys.executable, "-m", "pytest", "test_calculator.py"],
        category=GateCategory.UNIT,
    )

    runner = ValidationRunner()
    completion_gate = CompletionGate()

    # Initial validation run -> must FAIL
    initial_source_version = hashlib.sha256(calc_file.read_bytes()).hexdigest()
    initial_val_result = runner.run_gate(
        gate=gate_def,
        task_id=task_id,
        scope=scope,
        source_version=initial_source_version,
    )

    assert initial_val_result.status == GateStatus.FAIL

    # Completion gate must DENY completion
    initial_comp_eval = completion_gate.evaluate_completion(
        task_id=task_id,
        required_gates=["unit_mult_test"],
        validation_results=[initial_val_result],
        current_source_version=initial_source_version,
    )
    assert initial_comp_eval.can_complete is False

    # 3. Recovery Lifecycle: diagnose and repair
    recovery_controller = RecoveryController()

    def apply_repair():
        calc_file.write_text(
            "def multiply(a, b):\n    return a * b  # Repaired\n",
            encoding="utf-8",
        )
        return "Changed '+' to '*' in calculator.py"

    recovery_outcome = recovery_controller.attempt_recovery(
        task_id=task_id,
        scope=scope,
        failure=initial_val_result,
        repair_action=apply_repair,
        retest_gates=[gate_def],
    )

    assert recovery_outcome.state == RecoveryState.RECOVERED
    assert recovery_outcome.success is True
    assert len(recovery_outcome.retest_results) == 1
    assert recovery_outcome.retest_results[0].status == GateStatus.PASS

    # 4. Final Completion Gate check with fresh validation evidence
    repaired_source_version = hashlib.sha256(calc_file.read_bytes()).hexdigest()
    final_val_result = runner.run_gate(
        gate=gate_def,
        task_id=task_id,
        scope=scope,
        source_version=repaired_source_version,
    )

    assert final_val_result.status == GateStatus.PASS

    final_comp_eval = completion_gate.evaluate_completion(
        task_id=task_id,
        required_gates=["unit_mult_test"],
        validation_results=[final_val_result],
        current_source_version=repaired_source_version,
    )

    assert final_comp_eval.can_complete is True
    assert "All required validation gates passed with fresh evidence." in final_comp_eval.reason
