"""Explicit agent behavior state loop with strict budgets (T069, T070, T071)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField

from coagent.agent.planner import ExecutionPlan, Planner
from coagent.context.contracts import ContextQuery, ContextStage
from coagent.context.engine import ContextEngine, ContextPackage
from coagent.execution.cancellation import CancellationToken, OperationCancelledError
from coagent.memory.manager import ScopedMemoryManager
from coagent.models.contracts import MessageRole, ModelMessage, ToolCallProposal
from coagent.models.gateway import ModelGateway
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequest,
    ToolRequestSource,
    ToolResult,
)
from coagent.tools.gateway import ToolGateway
from coagent.workspace.scope import WorkspaceScope


class AgentState(StrEnum):
    """Lifecycle state machine for the Co-Agent reasoning and execution loop."""

    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    OBSERVING = "OBSERVING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentLoopBudget(BaseModel):
    """Deterministic loop bounds preventing infinite reasoning or action loops (T070)."""

    model_config = ConfigDict(extra="forbid")

    max_turns: int = PydanticField(default=25, ge=1)
    max_tool_calls: int = PydanticField(default=50, ge=1)
    max_consecutive_failures: int = PydanticField(default=3, ge=1)
    max_recovery_attempts: int = PydanticField(default=3, ge=0)


@dataclass
class AgentLoopMetrics:
    """Telemetry tracking loop resource consumption."""

    turns_executed: int = 0
    tool_calls_executed: int = 0
    tool_calls_failed: int = 0
    consecutive_failures: int = 0
    recovery_attempts: int = 0


@dataclass
class AgentResult:
    """Outcome of an agent execution cycle."""

    state: AgentState
    summary: str
    plan: ExecutionPlan | None
    metrics: AgentLoopMetrics
    observations: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None


class AgentLoop:
    """Controlled behavioral loop executing tasks through policy-governed tools."""

    def __init__(
        self,
        task_id: UUID,
        workspace_scope: WorkspaceScope,
        model_gateway: ModelGateway,
        tool_gateway: ToolGateway,
        context_engine: ContextEngine,
        autonomy_mode: AutonomyMode = AutonomyMode.ASSISTED_IMPLEMENT,
        planner: Planner | None = None,
        memory_manager: ScopedMemoryManager | None = None,
        budget: AgentLoopBudget | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> None:
        self.task_id = task_id
        self.workspace_scope = workspace_scope
        self.model = model_gateway
        self.tools = tool_gateway
        self.context = context_engine
        self.autonomy_mode = autonomy_mode
        self.planner = planner or Planner(model_gateway)
        self.memory = memory_manager
        self.budget = budget or AgentLoopBudget()
        self.cancellation_token = cancellation_token
        self.state = AgentState.IDLE
        self.metrics = AgentLoopMetrics()
        self.plan: ExecutionPlan | None = None
        self.observations: list[dict[str, Any]] = []

    def run(self, requirement: str) -> AgentResult:
        """Run the bounded agent lifecycle from understanding to completion."""
        self.state = AgentState.UNDERSTANDING

        try:
            # 1. UNDERSTANDING & PLANNING
            self._check_cancellation()
            plan_context = self.context.assemble_context(
                ContextQuery(
                    task_id=self.task_id,
                    stage=ContextStage.PLANNING,
                    workspace_scope=self.workspace_scope,
                )
            )

            self.state = AgentState.PLANNING
            self.plan = self.planner.create_plan(
                task_requirement=requirement,
                context_package=plan_context,
                scope=self.workspace_scope,
            )

            # 2. EXECUTION & OBSERVATION LOOP
            self.state = AgentState.EXECUTING

            while not self.plan.is_finished:
                self._check_cancellation()
                self._check_budgets()

                self.metrics.turns_executed += 1
                curr_step = self.plan.current_step
                if curr_step is None:
                    break

                # Assemble fresh stage context
                exec_context = self.context.assemble_context(
                    ContextQuery(
                        task_id=self.task_id,
                        stage=ContextStage.IMPLEMENTATION,
                        workspace_scope=self.workspace_scope,
                        target_files=curr_step.target_files,
                    )
                )

                # Query model for step execution actions
                model_response = self._query_model_for_step(
                    requirement, curr_step.description, exec_context
                )

                if model_response.tool_calls:
                    # Execute proposed tool calls through gateway
                    step_success = True
                    for proposal in model_response.tool_calls:
                        self._check_cancellation()
                        if self.metrics.tool_calls_executed >= self.budget.max_tool_calls:
                            max_calls = self.budget.max_tool_calls
                            raise RuntimeError(
                                f"Agent exceeded maximum tool call budget ({max_calls})"
                            )

                        tool_res = self._execute_tool_proposal(proposal)
                        self.metrics.tool_calls_executed += 1

                        # T071: Incorporate observation into context
                        self.state = AgentState.OBSERVING
                        obs_record = {
                            "turn": self.metrics.turns_executed,
                            "step_id": curr_step.step_id,
                            "tool": proposal.name,
                            "arguments": proposal.arguments,
                            "success": tool_res.success,
                            "output": tool_res.output,
                            "error": tool_res.error.message if tool_res.error else None,
                        }
                        self.observations.append(obs_record)

                        if not tool_res.success:
                            step_success = False
                            self.metrics.tool_calls_failed += 1
                            self.metrics.consecutive_failures += 1
                            if (
                                self.metrics.consecutive_failures
                                >= self.budget.max_consecutive_failures
                            ):
                                raise RuntimeError(
                                    f"Agent reached consecutive failure limit "
                                    f"({self.budget.max_consecutive_failures})"
                                )
                        else:
                            self.metrics.consecutive_failures = 0

                    if step_success:
                        self.plan.mark_step_completed(curr_step.step_id)
                    else:
                        self.plan.mark_step_failed(curr_step.step_id)
                else:
                    # No tool calls proposed: model concluded step
                    self.plan.mark_step_completed(curr_step.step_id)

            self.state = AgentState.COMPLETED
            return AgentResult(
                state=self.state,
                summary="Task completed successfully.",
                plan=self.plan,
                metrics=self.metrics,
                observations=self.observations,
            )

        except OperationCancelledError:
            self.state = AgentState.CANCELLED
            return AgentResult(
                state=self.state,
                summary="Task was cancelled by user.",
                plan=self.plan,
                metrics=self.metrics,
                observations=self.observations,
                error_message="Operation cancelled",
            )
        except Exception as exc:
            self.state = AgentState.FAILED
            return AgentResult(
                state=self.state,
                summary=f"Task failed: {exc}",
                plan=self.plan,
                metrics=self.metrics,
                observations=self.observations,
                error_message=str(exc),
            )

    def _query_model_for_step(
        self,
        requirement: str,
        step_description: str,
        context: ContextPackage,
    ) -> Any:
        messages = [
            ModelMessage(
                role=MessageRole.SYSTEM,
                content="You are the execution agent. Use available tools to accomplish the step.",
            ),
            ModelMessage(
                role=MessageRole.USER,
                content=(
                    f"TASK: {requirement}\n"
                    f"CURRENT STEP: {step_description}\n\n"
                    f"CONTEXT:\n{context.formatted_prompt}\n"
                ),
            ),
        ]
        return self.model.generate(messages, temperature=0.1)

    def _execute_tool_proposal(self, proposal: ToolCallProposal) -> ToolResult:
        """Route tool proposal through central ToolGateway and PolicyEngine."""
        canonical_scope = Scope(
            workspace_id=self.workspace_scope.workspace_id,
            root=self.workspace_scope.root,
        )

        # Look up tool definition version from registry
        tool_def = self.tools._registry.get(proposal.name)
        tool_version = tool_def.version if tool_def else "1.0"

        req = ToolRequest(
            request_id=uuid4(),
            task_id=self.task_id,
            correlation_id=uuid4(),
            tool_id=proposal.name,
            tool_version=tool_version,
            arguments=proposal.arguments,
            requested_scope=canonical_scope,
            autonomy_mode=self.autonomy_mode,
            source=ToolRequestSource.AGENT,
            created_at=datetime.now(UTC),
        )

        return self.tools.route(req)

    def _check_cancellation(self) -> None:
        if self.cancellation_token is not None:
            self.cancellation_token.check()

    def _check_budgets(self) -> None:
        if self.metrics.turns_executed >= self.budget.max_turns:
            raise RuntimeError(
                f"Agent exceeded maximum turn budget ({self.budget.max_turns})"
            )
