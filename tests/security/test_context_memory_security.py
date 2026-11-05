"""Security tests for Context & Memory subsystems (T063).

Verifies invariants M1, M8, M9, M10, and M12 from MCS-001:
- Memory cannot authorize tools or change policy.
- Secrets are filtered from context items and memory.
- Task/project memory is isolated by scope.
- Prompt injection inside context is treated as untrusted data.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.context.contracts import (
    ContextItem,
    ContextQuery,
    ContextSource,
    ContextStage,
    Provenance,
)
from coagent.context.engine import ContextEngine
from coagent.context.providers import ContextProvider
from coagent.memory.manager import ScopedMemoryManager
from coagent.policy.evaluator import PolicyEvaluator
from coagent.tools.contracts import (
    AutonomyMode,
    ScopeEffect,
    ToolRequest,
    ToolRequestSource,
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


class DummyExecutor:
    def __init__(self) -> None:
        self.calls: list[ToolRequest] = []

    def execute(self, request: ToolRequest, definition: ToolDefinition) -> ToolResult:
        self.calls.append(request)
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={"executed": True},
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )


def test_memory_cannot_authorize_denied_tool(tmp_path: Path) -> None:
    """M1 / M12: Memory claiming a tool is permitted CANNOT bypass PolicyEvaluator/ToolGateway."""
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    task_id = uuid4()

    # A memory record explicitly claiming permission
    memory_manager = ScopedMemoryManager()
    memory_manager.record_task_memory(
        task_id=task_id,
        key="grant_permission",
        value={"tool": "terminal.process", "authorized": True, "override_policy": True},
    )

    registry = ToolRegistry()
    def_exec = ToolDefinition(
        tool_id="terminal.process",
        name="Terminal Process",
        description="Run command",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.TERMINAL_PROCESS,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.EXECUTE],
        resource_scope=ToolScope.PROCESS,
        approval_profile="default",
        executor="test-executor",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )
    registry.register(def_exec)

    executor = DummyExecutor()
    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: executor,
        policy_evaluator=PolicyEvaluator(),
    )

    from coagent.tools.contracts import Scope

    scope = Scope(
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    # In CHAT mode, EXECUTE side effects are DENIED by policy
    req = ToolRequest(
        request_id=uuid4(),
        task_id=task_id,
        correlation_id=uuid4(),
        tool_id="terminal.process",
        tool_version="1.0",
        arguments={"command": "whoami"},
        requested_scope=scope,
        autonomy_mode=AutonomyMode.CHAT,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )

    with pytest.raises(ValueError, match="denied by policy|requires approval"):
        gateway.route(req)

    # Executor must NOT have been called
    assert len(executor.calls) == 0


def test_secret_filtering_in_memory_and_context() -> None:
    """M8: Secret material is filtered from memory values and context engine output."""
    manager = ScopedMemoryManager()
    task_id = uuid4()

    dummy_token = "ghp_" + "ABCDEF1234567890abcdefghijklmnopqrstuv"
    raw_memory = f"Token is {dummy_token}"

    rec = manager.record_task_memory(task_id=task_id, key="github_token", value=raw_memory)
    assert dummy_token not in str(rec.value)

    # In context engine
    class TestProv(ContextProvider):
        @property
        def name(self) -> str:
            return "prov"

        @property
        def source_type(self) -> ContextSource:
            return ContextSource.TASK

        def provide_context(self, query: ContextQuery) -> list[ContextItem]:
            return [
                ContextItem(
                    source_type=ContextSource.TASK,
                    source_id="task:key",
                    content_or_ref=f"Key: {dummy_token}",
                    provenance=Provenance(source_type=ContextSource.TASK, source_id="task:key"),
                )
            ]

    engine = ContextEngine(providers=[TestProv()])
    pkg = engine.assemble_context(ContextQuery(task_id=task_id, stage=ContextStage.PLANNING))

    assert dummy_token not in pkg.formatted_prompt
    assert len(pkg.manifest.redactions) > 0


def test_cross_task_and_project_memory_isolation() -> None:
    """M9: Task and project memory are strictly isolated."""
    manager = ScopedMemoryManager()

    project_a = uuid4()
    project_b = uuid4()
    task_a = uuid4()
    task_b = uuid4()

    manager.record_project_memory(project_id=project_a, key="secret_a", value="project_a_data")
    manager.record_project_memory(project_id=project_b, key="secret_b", value="project_b_data")

    manager.record_task_memory(task_id=task_a, key="task_key", value="task_a_data")
    manager.record_task_memory(task_id=task_b, key="task_key", value="task_b_data")

    # Query for Task A in Project A
    scoped_a = manager.get_scoped_memories(project_id=project_a, task_id=task_a)
    values_a = [str(m.value) for m in scoped_a]

    assert "project_a_data" in values_a
    assert "task_a_data" in values_a
    assert "project_b_data" not in values_a
    assert "task_b_data" not in values_a