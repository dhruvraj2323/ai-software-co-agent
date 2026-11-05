"""Execution planning contracts and Planner implementation (T068)."""

from __future__ import annotations

import json
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from coagent.context.engine import ContextPackage
from coagent.models.contracts import MessageRole, ModelMessage
from coagent.models.gateway import ModelGateway
from coagent.workspace.scope import WorkspaceScope


class StepStatus(StrEnum):
    """Execution status of an individual plan step."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class PlanStep(BaseModel):
    """An atomic, ordered unit of execution within an ExecutionPlan."""

    model_config = ConfigDict(extra="forbid")

    step_id: int
    description: str
    target_files: list[str] = Field(default_factory=list)
    expected_action: str = "EDIT"
    status: StepStatus = StepStatus.PENDING


class ExecutionPlan(BaseModel):
    """Structured plan decomposing task requirements into verified steps."""

    model_config = ConfigDict(extra="forbid")

    plan_id: UUID = Field(default_factory=uuid4)
    goal: str
    steps: list[PlanStep]
    validation_criteria: list[str]
    risks: list[str] = Field(default_factory=list)
    version: int = 1
    current_step_index: int = 0

    @property
    def is_finished(self) -> bool:
        """Return True if all steps are completed or skipped."""
        return all(s.status in {StepStatus.COMPLETED, StepStatus.SKIPPED} for s in self.steps)

    @property
    def current_step(self) -> PlanStep | None:
        """Return the currently active step if any."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def mark_step_completed(self, step_id: int) -> None:
        """Mark a step completed and advance pointer."""
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                self.steps[i] = step.model_copy(update={"status": StepStatus.COMPLETED})
                self.current_step_index = i + 1
                break

    def mark_step_failed(self, step_id: int) -> None:
        """Mark a step failed."""
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                self.steps[i] = step.model_copy(update={"status": StepStatus.FAILED})
                break


class Planner:
    """Plans and revises execution steps consuming controlled context packages."""

    def __init__(self, model_gateway: ModelGateway | None = None) -> None:
        self._model = model_gateway or ModelGateway()

    def create_plan(
        self,
        task_requirement: str,
        context_package: ContextPackage,
        scope: WorkspaceScope | None = None,
    ) -> ExecutionPlan:
        """Generate an execution plan consuming controlled context."""
        prompt = (
            "You are the Planning module. Given the task and context, generate a "
            "JSON plan with keys: 'goal', 'steps', 'validation_criteria', 'risks'.\n\n"
            f"TASK REQUIREMENT:\n{task_requirement}\n\n"
            f"CONTEXT:\n{context_package.formatted_prompt}\n"
        )

        messages = [
            ModelMessage(role=MessageRole.SYSTEM, content="You produce valid JSON plans only."),
            ModelMessage(role=MessageRole.USER, content=prompt),
        ]

        response = self._model.generate(messages, temperature=0.1)
        plan = self._parse_plan_json(response.content, fallback_goal=task_requirement)

        if scope is not None:
            self._validate_plan_scope(plan, scope)

        return plan

    def revise_plan(
        self,
        current_plan: ExecutionPlan,
        new_context: ContextPackage,
        blocker_reason: str,
    ) -> ExecutionPlan:
        """Revise an existing plan after an execution failure or unexpected observation."""
        prompt = (
            f"The execution encountered a blocker:\n{blocker_reason}\n\n"
            f"CURRENT PLAN (v{current_plan.version}):\n{current_plan.model_dump_json(indent=2)}\n\n"
            f"FRESH CONTEXT:\n{new_context.formatted_prompt}\n\n"
            f"Produce a revised JSON plan with new or adjusted steps."
        )

        messages = [
            ModelMessage(role=MessageRole.SYSTEM, content="You produce valid JSON plans only."),
            ModelMessage(role=MessageRole.USER, content=prompt),
        ]

        response = self._model.generate(messages, temperature=0.1)
        revised = self._parse_plan_json(response.content, fallback_goal=current_plan.goal)
        return revised.model_copy(update={"version": current_plan.version + 1})

    def _parse_plan_json(self, content: str, fallback_goal: str) -> ExecutionPlan:
        try:
            # Strip markdown code blocks if present
            clean = content.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            data = json.loads(clean.strip())

            steps: list[PlanStep] = []
            for i, s in enumerate(data.get("steps", []), start=1):
                steps.append(
                    PlanStep(
                        step_id=i,
                        description=s.get("description", f"Step {i}"),
                        target_files=s.get("target_files", []),
                        expected_action=s.get("expected_action", "EDIT"),
                    )
                )

            if not steps:
                steps = [
                    PlanStep(step_id=1, description="Inspect repo", expected_action="READ"),
                    PlanStep(step_id=2, description="Implement changes", expected_action="EDIT"),
                    PlanStep(step_id=3, description="Validate", expected_action="VALIDATE"),
                ]

            return ExecutionPlan(
                goal=data.get("goal", fallback_goal),
                steps=steps,
                validation_criteria=data.get("validation_criteria", ["Pass unit tests"]),
                risks=data.get("risks", []),
            )
        except Exception:
            # Deterministic default fallback plan
            return ExecutionPlan(
                goal=fallback_goal,
                steps=[
                    PlanStep(step_id=1, description="Inspect files", expected_action="READ"),
                    PlanStep(step_id=2, description="Apply changes", expected_action="EDIT"),
                    PlanStep(step_id=3, description="Run validation", expected_action="VALIDATE"),
                ],
                validation_criteria=["Pass automated test suite"],
                risks=[],
            )

    def _validate_plan_scope(self, plan: ExecutionPlan, scope: WorkspaceScope) -> None:
        """Ensure planned target files do not escape the workspace boundary."""
        from coagent.security.path import is_path_within_workspace

        for step in plan.steps:
            for file_path in step.target_files:
                if not is_path_within_workspace(scope, file_path):
                    raise ValueError(
                        f"Plan step {step.step_id} targets path outside authorized workspace: "
                        f"'{file_path}'"
                    )
