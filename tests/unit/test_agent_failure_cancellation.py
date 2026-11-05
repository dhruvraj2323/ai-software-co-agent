"""Tests for Agent failure handling, budget limits, and cancellation (T070, T073)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from coagent.agent.loop import AgentLoop, AgentLoopBudget, AgentState
from coagent.context.engine import ContextEngine
from coagent.execution.cancellation import CancellationToken
from coagent.models.adapter import MockModelAdapter
from coagent.models.contracts import ModelResponse
from coagent.models.gateway import ModelGateway
from coagent.policy.evaluator import PolicyEvaluator
from coagent.tools.gateway import ToolGateway
from coagent.tools.registry import (
    ToolRegistry,
)
from coagent.workspace.scope import WorkspaceScope


def test_agent_cancellation_stops_execution(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    token = CancellationToken()
    token.cancel()  # Pre-cancelled

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    registry = ToolRegistry()
    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: None,  # type: ignore[arg-type]
        policy_evaluator=PolicyEvaluator(),
    )

    loop = AgentLoop(
        task_id=scope.task_id,
        workspace_scope=scope,
        model_gateway=ModelGateway(),
        tool_gateway=gateway,
        context_engine=ContextEngine(),
        cancellation_token=token,
    )

    result = loop.run("Any task")
    assert result.state == AgentState.CANCELLED
    assert result.error_message == "Operation cancelled"


def test_agent_turn_budget_limit_exhaustion(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    registry = ToolRegistry()
    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: None,  # type: ignore[arg-type]
        policy_evaluator=PolicyEvaluator(),
    )

    mock_adapter = MockModelAdapter()
    plan_json = json.dumps({
        "goal": "Loop forever",
        "steps": [
            {"description": f"Step {i}", "expected_action": "EDIT"} for i in range(10)
        ],
    })
    mock_adapter.queue_response(ModelResponse(content=plan_json))

    # Queue endless empty responses that keep repeating
    loop = AgentLoop(
        task_id=scope.task_id,
        workspace_scope=scope,
        model_gateway=ModelGateway(default_adapter=mock_adapter),
        tool_gateway=gateway,
        context_engine=ContextEngine(),
        budget=AgentLoopBudget(max_turns=2),
    )

    result = loop.run("Infinite turns")
    assert result.state == AgentState.FAILED
    assert "exceeded maximum turn budget" in (result.error_message or "")


def test_agent_model_provider_failure_stops_safely(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    registry = ToolRegistry()
    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: None,  # type: ignore[arg-type]
        policy_evaluator=PolicyEvaluator(),
    )

    def crashing_generator(messages):
        raise ConnectionError("Upstream LLM API connection timed out")

    mock_adapter = MockModelAdapter(generator=crashing_generator)

    loop = AgentLoop(
        task_id=scope.task_id,
        workspace_scope=scope,
        model_gateway=ModelGateway(default_adapter=mock_adapter),
        tool_gateway=gateway,
        context_engine=ContextEngine(),
    )

    result = loop.run("Task with failing model")
    assert result.state == AgentState.FAILED
    assert "Upstream LLM API connection timed out" in (result.error_message or "")
