"""Unit and behavioral tests for Agent state loop and tool execution (T069, T071, T072)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.agent.loop import AgentLoop, AgentState
from coagent.context.engine import ContextEngine
from coagent.context.providers import TaskContextProvider
from coagent.models.adapter import MockModelAdapter
from coagent.models.contracts import ModelResponse, ToolCallProposal
from coagent.models.gateway import ModelGateway
from coagent.policy.evaluator import PolicyEvaluator
from coagent.tools.contracts import (
    ScopeEffect,
    ToolRequest,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.gateway import ToolGateway
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRegistry,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.workspace.scope import WorkspaceScope


class DummyToolExecutor:
    def __init__(self) -> None:
        self.invocations: list[ToolRequest] = []

    def execute(self, request: ToolRequest, definition: ToolDefinition) -> ToolResult:
        self.invocations.append(request)
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={"result": f"Executed {definition.tool_id} on {request.arguments}"},
            scope_effect=ScopeEffect.MODIFIED,
            created_at=datetime.now(UTC),
        )


def test_agent_loop_lifecycle_and_tool_incorporation(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(workspace_dir))

    # 1. Setup tool registry with read tool
    registry = ToolRegistry()
    read_def = ToolDefinition(
        tool_id="workspace.read_file",
        name="Read File",
        description="Read file contents",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="dummy",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )
    registry.register(read_def)

    executor = DummyToolExecutor()
    tool_gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: executor,
        policy_evaluator=PolicyEvaluator(),
    )

    # 2. Setup mock model adapter:
    # First response: Plan JSON
    # Second response: Tool call proposal to read file
    # Third response: Finish step
    mock_adapter = MockModelAdapter()

    plan_json = json.dumps({
        "goal": "Inspect configuration",
        "steps": [
            {
                "description": "Read config file",
                "target_files": ["config.py"],
                "expected_action": "READ",
            },
        ],
        "validation_criteria": ["Config verified"],
    })
    mock_adapter.queue_response(ModelResponse(content=plan_json))

    # Step execution response proposing tool call
    tool_proposal = ToolCallProposal(
        name="workspace.read_file",
        arguments={"path": "config.py"},
    )
    mock_adapter.queue_response(
        ModelResponse(
            content="Reading configuration.",
            tool_calls=[tool_proposal],
        )
    )

    model_gateway = ModelGateway(default_adapter=mock_adapter)
    ctx_provider = TaskContextProvider({"requirement": "Inspect config"})
    context_engine = ContextEngine(providers=[ctx_provider])

    loop = AgentLoop(
        task_id=task_id,
        workspace_scope=scope,
        model_gateway=model_gateway,
        tool_gateway=tool_gateway,
        context_engine=context_engine,
    )

    result = loop.run(requirement="Inspect config")

    assert result.state == AgentState.COMPLETED
    assert result.plan is not None
    assert result.plan.is_finished is True
    assert len(executor.invocations) == 1
    assert executor.invocations[0].tool_id == "workspace.read_file"

    # T071: Verify observation incorporation
    assert len(result.observations) == 1
    obs = result.observations[0]
    assert obs["tool"] == "workspace.read_file"
    assert obs["success"] is True
    assert "Executed workspace.read_file" in str(obs["output"])
    assert result.metrics.turns_executed >= 1
    assert result.metrics.tool_calls_executed == 1
