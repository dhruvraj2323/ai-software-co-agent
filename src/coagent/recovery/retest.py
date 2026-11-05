"""Retest workflow executing targeted validation after repairs (ERS-001 §12)."""

from __future__ import annotations

from uuid import UUID

from coagent.validation.evidence import ValidationResult
from coagent.validation.runner import ValidationGateDefinition, ValidationRunner
from coagent.workspace.scope import WorkspaceScope


class RetestWorkflow:
    """Executes validation gates to verify whether repairs successfully resolved failures."""

    def __init__(self, runner: ValidationRunner | None = None) -> None:
        self._runner = runner or ValidationRunner()

    def run_retest(
        self,
        task_id: UUID,
        scope: WorkspaceScope,
        gates: list[ValidationGateDefinition],
        source_version: str | None = None,
    ) -> list[ValidationResult]:
        """Execute all relevant validation gates and collect fresh results."""
        results: list[ValidationResult] = []
        for gate in gates:
            res = self._runner.run_gate(
                gate=gate,
                task_id=task_id,
                scope=scope,
                source_version=source_version,
            )
            results.append(res)
        return results

    def is_successful(self, results: list[ValidationResult]) -> bool:
        """Return True only if every executed validation gate passed cleanly."""
        return bool(results) and all(r.is_pass for r in results)
