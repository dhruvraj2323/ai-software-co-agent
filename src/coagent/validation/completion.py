"""Authoritative Completion Gate evaluating required validation evidence (TVS-001 §18)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.validation.evidence import GateStatus, ValidationResult


class CompletionEvaluation(BaseModel):
    """Authoritative decision on whether a task may enter the COMPLETE state."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    can_complete: bool
    reason: str
    required_gates: list[str]
    passed_gates: list[str]
    failed_gates: list[str]
    missing_gates: list[str]
    stale_gates: list[str]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CompletionGate:
    """Authoritative validation gate: no task can complete without required evidence."""

    def evaluate_completion(
        self,
        task_id: UUID,
        required_gates: list[str],
        validation_results: list[ValidationResult],
        current_source_version: str | None = None,
    ) -> CompletionEvaluation:
        """Evaluate whether current validation evidence satisfies completion requirements."""
        if not required_gates:
            return CompletionEvaluation(
                task_id=task_id,
                can_complete=False,
                reason="Completion denied: no required validation gates defined.",
                required_gates=[],
                passed_gates=[],
                failed_gates=[],
                missing_gates=[],
                stale_gates=[],
            )

        # Index latest result per gate
        latest_results: dict[str, ValidationResult] = {}
        for r in validation_results:
            if r.task_id == task_id:
                latest_results[r.gate_id] = r

        passed: list[str] = []
        failed: list[str] = []
        missing: list[str] = []
        stale: list[str] = []

        for gate in required_gates:
            result = latest_results.get(gate)
            if result is None:
                missing.append(gate)
                continue

            if result.status != GateStatus.PASS:
                failed.append(gate)
                continue

            # Check freshness: if source version changed after validation was run, result is stale
            if (
                current_source_version is not None
                and result.source_version is not None
                and result.source_version != current_source_version
            ):
                stale.append(gate)
                continue

            passed.append(gate)

        can_complete = (len(passed) == len(required_gates)) and not (failed or missing or stale)

        if can_complete:
            reason = "All required validation gates passed with fresh evidence."
        else:
            blockers: list[str] = []
            if missing:
                blockers.append(f"Missing required gates: {', '.join(missing)}")
            if failed:
                blockers.append(f"Failed gates: {', '.join(failed)}")
            if stale:
                blockers.append(f"Stale validation evidence: {', '.join(stale)}")
            reason = f"Completion blocked: {'; '.join(blockers)}"

        return CompletionEvaluation(
            task_id=task_id,
            can_complete=can_complete,
            reason=reason,
            required_gates=required_gates,
            passed_gates=passed,
            failed_gates=failed,
            missing_gates=missing,
            stale_gates=stale,
        )
