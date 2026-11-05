"""Adversarial security tests for Completion Gate false-completion prevention (T083)."""

from __future__ import annotations

from uuid import uuid4

from coagent.validation.completion import CompletionGate
from coagent.validation.evidence import GateStatus, ValidationResult


def test_completion_fails_with_no_validation_evidence() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT"],
        validation_results=[],  # Zero evidence
    )

    assert eval_res.can_complete is False
    assert "Missing required gates: G1_UNIT" in eval_res.reason


def test_completion_fails_with_failing_gate_evidence() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    failing_result = ValidationResult(
        gate_id="G1_UNIT",
        task_id=task_id,
        command="pytest",
        status=GateStatus.FAIL,
    )

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT"],
        validation_results=[failing_result],
    )

    assert eval_res.can_complete is False
    assert "Failed gates: G1_UNIT" in eval_res.reason


def test_completion_fails_with_stale_source_version() -> None:
    """Adversarial test: attacker passes tests, edits code maliciously, tries to complete."""
    gate = CompletionGate()
    task_id = uuid4()

    test_passed_result = ValidationResult(
        gate_id="G1_UNIT",
        task_id=task_id,
        command="pytest",
        status=GateStatus.PASS,
        source_version="clean_sha_aaa",
    )

    # Repository code was modified afterwards to dirty_sha_bbb
    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT"],
        validation_results=[test_passed_result],
        current_source_version="dirty_sha_bbb",
    )

    assert eval_res.can_complete is False
    assert "Stale validation evidence: G1_UNIT" in eval_res.reason


def test_completion_fails_when_any_required_gate_is_blocked() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    results = [
        ValidationResult(
            gate_id="G1_UNIT",
            task_id=task_id,
            command="pytest",
            status=GateStatus.PASS,
        ),
        ValidationResult(
            gate_id="G4_SECURITY",
            task_id=task_id,
            command="security_scan",
            status=GateStatus.BLOCKED,
        ),
    ]

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT", "G4_SECURITY"],
        validation_results=results,
    )

    assert eval_res.can_complete is False
    assert "G4_SECURITY" in eval_res.failed_gates
