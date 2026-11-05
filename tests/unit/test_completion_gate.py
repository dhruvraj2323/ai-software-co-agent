"""Unit tests for authoritative CompletionGate (T078)."""

from __future__ import annotations

from uuid import uuid4

from coagent.validation.completion import CompletionGate
from coagent.validation.evidence import GateStatus, ValidationResult


def test_completion_gate_approves_when_all_required_gates_pass() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    results = [
        ValidationResult(
            gate_id="G1_UNIT",
            task_id=task_id,
            command="pytest",
            status=GateStatus.PASS,
            source_version="commit_sha_123",
        ),
        ValidationResult(
            gate_id="G4_SECURITY",
            task_id=task_id,
            command="security_scan",
            status=GateStatus.PASS,
            source_version="commit_sha_123",
        ),
    ]

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT", "G4_SECURITY"],
        validation_results=results,
        current_source_version="commit_sha_123",
    )

    assert eval_res.can_complete is True
    assert len(eval_res.passed_gates) == 2
    assert len(eval_res.failed_gates) == 0
    assert len(eval_res.missing_gates) == 0
    assert len(eval_res.stale_gates) == 0


def test_completion_gate_rejects_missing_required_gate() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    results = [
        ValidationResult(
            gate_id="G1_UNIT",
            task_id=task_id,
            command="pytest",
            status=GateStatus.PASS,
        ),
    ]

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT", "G4_SECURITY"],  # G4 is missing!
        validation_results=results,
    )

    assert eval_res.can_complete is False
    assert "G4_SECURITY" in eval_res.missing_gates


def test_completion_gate_rejects_failing_gate() -> None:
    gate = CompletionGate()
    task_id = uuid4()

    results = [
        ValidationResult(
            gate_id="G1_UNIT",
            task_id=task_id,
            command="pytest",
            status=GateStatus.FAIL,
        ),
    ]

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT"],
        validation_results=results,
    )

    assert eval_res.can_complete is False
    assert "G1_UNIT" in eval_res.failed_gates


def test_completion_gate_rejects_stale_validation_evidence() -> None:
    """If repository code was modified after validation ran, validation is stale."""
    gate = CompletionGate()
    task_id = uuid4()

    results = [
        ValidationResult(
            gate_id="G1_UNIT",
            task_id=task_id,
            command="pytest",
            status=GateStatus.PASS,
            source_version="old_hash_111",
        ),
    ]

    eval_res = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["G1_UNIT"],
        validation_results=results,
        current_source_version="new_hash_222",  # Code modified since test ran!
    )

    assert eval_res.can_complete is False
    assert "G1_UNIT" in eval_res.stale_gates
