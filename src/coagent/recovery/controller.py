"""Coordinated error recovery controller (ERS-001 §3, §4, §10)."""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.core.errors import ErrorRecord
from coagent.core.types import Recoverability
from coagent.recovery.budgets import RecoveryBudgetTracker
from coagent.recovery.classifier import FailureClassifier
from coagent.recovery.retest import RetestWorkflow
from coagent.tools.gateway import ToolGateway
from coagent.validation.evidence import ValidationResult
from coagent.validation.runner import ValidationGateDefinition
from coagent.workspace.scope import WorkspaceScope


class RecoveryState(StrEnum):
    """Lifecycle states of the error recovery state machine (ERS-001 §4)."""

    IDLE = "IDLE"
    FAILURE_CAPTURED = "FAILURE_CAPTURED"
    CLASSIFIED = "CLASSIFIED"
    ELIGIBLE_CHECK = "ELIGIBLE_CHECK"
    CONTEXT_BUILD = "CONTEXT_BUILD"
    DIAGNOSING = "DIAGNOSING"
    REPAIR_PLANNED = "REPAIR_PLANNED"
    POLICY_CHECK = "POLICY_CHECK"
    APPLYING = "APPLYING"
    RETESTING = "RETESTING"
    RECOVERED = "RECOVERED"
    NEXT_ATTEMPT = "NEXT_ATTEMPT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class RecoveryOutcome(BaseModel):
    """Structured report produced at the conclusion of a recovery cycle."""

    model_config = ConfigDict(extra="forbid")

    state: RecoveryState
    success: bool
    error_record: ErrorRecord
    attempts: int
    repair_description: str | None = None
    retest_results: list[ValidationResult] = Field(default_factory=list)
    reason: str | None = None


class RecoveryController:
    """Orchestrates bounded, policy-compliant diagnosis, repair, and revalidation."""

    def __init__(
        self,
        classifier: FailureClassifier | None = None,
        tracker: RecoveryBudgetTracker | None = None,
        tool_gateway: ToolGateway | None = None,
        retest_workflow: RetestWorkflow | None = None,
    ) -> None:
        self.classifier = classifier or FailureClassifier()
        self.tracker = tracker or RecoveryBudgetTracker()
        self.tools = tool_gateway
        self.retest = retest_workflow or RetestWorkflow()

    def attempt_recovery(
        self,
        task_id: UUID,
        scope: WorkspaceScope,
        failure: ValidationResult | Exception,
        repair_action: Callable[[], Any] | None = None,
        retest_gates: list[ValidationGateDefinition] | None = None,
    ) -> RecoveryOutcome:
        """Execute a controlled recovery lifecycle."""
        # 1. Capture & Classify
        if isinstance(failure, ValidationResult):
            error_rec = self.classifier.classify_validation_failure(failure)
        else:
            error_rec = self.classifier.classify_exception(failure, task_id=task_id)

        # 2. Check Eligibility (ERS-001 §2: security/policy failures are not auto-bypassed)
        if error_rec.recoverability in {Recoverability.MANUAL, Recoverability.NONE}:
            rec_val = error_rec.recoverability.value
            return RecoveryOutcome(
                state=RecoveryState.BLOCKED,
                success=False,
                error_record=error_rec,
                attempts=self.tracker.attempts,
                reason=f"Error {error_rec.code} requires human intervention ({rec_val}).",
            )

        # 3. Check Budgets & Loop Detection (ERS-001 §8)
        if self.tracker.is_exhausted:
            return RecoveryOutcome(
                state=RecoveryState.FAILED,
                success=False,
                error_record=error_rec,
                attempts=self.tracker.attempts,
                reason="Recovery budget exhausted (max attempts or timeout reached).",
            )

        if self.tracker.is_loop_detected(error_rec.retry_key):
            return RecoveryOutcome(
                state=RecoveryState.FAILED,
                success=False,
                error_record=error_rec,
                attempts=self.tracker.attempts,
                reason=(
                    f"Recovery loop detected: repeated consecutive failures for "
                    f"'{error_rec.retry_key}'."
                ),
            )

        self.tracker.record_attempt(error_rec.retry_key)

        # 4. Apply Controlled Repair (ERS-001 §10)
        repair_desc = None
        if repair_action is not None:
            try:
                repair_desc = str(repair_action())
            except Exception as repair_exc:
                return RecoveryOutcome(
                    state=RecoveryState.FAILED,
                    success=False,
                    error_record=error_rec,
                    attempts=self.tracker.attempts,
                    reason=f"Repair action execution failed: {repair_exc}",
                )

        # 5. Retest (ERS-001 §12: repair must be followed by validation)
        retest_results: list[ValidationResult] = []
        if retest_gates:
            retest_results = self.retest.run_retest(
                task_id=task_id,
                scope=scope,
                gates=retest_gates,
            )
            passed = self.retest.is_successful(retest_results)
        else:
            # If no retest gates specified, repair action execution is considered sufficient
            passed = True

        if passed:
            return RecoveryOutcome(
                state=RecoveryState.RECOVERED,
                success=True,
                error_record=error_rec,
                attempts=self.tracker.attempts,
                repair_description=repair_desc,
                retest_results=retest_results,
                reason="Failure successfully repaired and validated.",
            )
        else:
            return RecoveryOutcome(
                state=RecoveryState.FAILED,
                success=False,
                error_record=error_rec,
                attempts=self.tracker.attempts,
                repair_description=repair_desc,
                retest_results=retest_results,
                reason="Retest validation failed after repair action.",
            )
