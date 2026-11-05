"""Unit tests for the agent execution Planner (T068)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.agent.planner import Planner, StepStatus
from coagent.context.engine import ContextPackage
from coagent.context.manifest import ContextManifest
from coagent.models.adapter import MockModelAdapter
from coagent.models.contracts import ModelResponse
from coagent.models.gateway import ModelGateway
from coagent.workspace.scope import WorkspaceScope


def make_dummy_context(task_id) -> ContextPackage:
    manifest = ContextManifest(
        task_id=task_id,
        stage="PLANNING",
        context_budget=5000,
        total_tokens=100,
        selected_items=[],
    )
    return ContextPackage(
        manifest=manifest,
        items=[],
        formatted_prompt="=== CONTEXT: REPOSITORY [repo:map] ===",
    )


def test_planner_creates_structured_plan() -> None:
    task_id = uuid4()
    mock_adapter = MockModelAdapter()

    plan_json = json.dumps({
        "goal": "Implement JWT auth",
        "steps": [
            {
                "description": "Create user model",
                "target_files": ["models.py"],
                "expected_action": "EDIT",
            },
            {
                "description": "Run tests",
                "target_files": ["tests/test_auth.py"],
                "expected_action": "VALIDATE",
            },
        ],
        "validation_criteria": ["All auth tests pass"],
        "risks": ["Secret leak risk"],
    })

    mock_adapter.queue_response(ModelResponse(content=plan_json))
    gateway = ModelGateway(default_adapter=mock_adapter)

    planner = Planner(gateway)
    context_pkg = make_dummy_context(task_id)

    plan = planner.create_plan(
        task_requirement="Implement JWT auth",
        context_package=context_pkg,
    )

    assert plan.goal == "Implement JWT auth"
    assert len(plan.steps) == 2
    assert plan.steps[0].target_files == ["models.py"]
    assert plan.current_step_index == 0
    assert plan.is_finished is False

    # Mark completed
    plan.mark_step_completed(1)
    assert plan.steps[0].status == StepStatus.COMPLETED
    assert plan.current_step_index == 1

    plan.mark_step_completed(2)
    assert plan.is_finished is True


def test_planner_enforces_workspace_scope_on_targets(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    mock_adapter = MockModelAdapter()
    escaping_plan_json = json.dumps({
        "goal": "Write outside workspace",
        "steps": [
            {
                "description": "Escape workspace",
                "target_files": ["../../etc/passwd"],
                "expected_action": "EDIT",
            }
        ],
    })
    mock_adapter.queue_response(ModelResponse(content=escaping_plan_json))
    gateway = ModelGateway(default_adapter=mock_adapter)

    planner = Planner(gateway)
    context_pkg = make_dummy_context(scope.task_id)

    with pytest.raises(ValueError, match="outside authorized workspace"):
        planner.create_plan(
            task_requirement="Malicious plan",
            context_package=context_pkg,
            scope=scope,
        )
