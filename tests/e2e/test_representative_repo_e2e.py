"""Representative Repository End-to-End Test Suite.

Verifies T111, ADM-001, Gate G10 according to:
- docs/specifications/09 AI_Software_CoAgent_Testing_Validation_Specification_v1.0_FINAL_LOCKED.md
- docs/project/18 AI_Software_CoAgent_Implementation_Plan_v1.0_FINAL_LOCKED.md
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.execution.filesystem import FilesystemExecutor
from coagent.execution.patch import (
    FilePatch,
    Patch,
    PatchEngine,
    PatchOperationType,
    compute_file_hash,
)
from coagent.recovery.controller import RecoveryController, RecoveryState
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequest,
    ToolRequestSource,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.validation.completion import CompletionGate
from coagent.validation.evidence import GateStatus
from coagent.validation.runner import ValidationGateDefinition, ValidationRunner
from coagent.workspace.scope import WorkspaceScope
from tests.fixtures.repo_fixtures import (
    create_broken_build_repo,
    create_minimal_python_repo,
    create_multi_module_repo,
)


def make_tool_def(
    tool_id: str,
    capability: ToolCapability,
    risk_level: ToolRiskLevel = ToolRiskLevel.MEDIUM,
    side_effects: list[ToolSideEffect] | None = None,
    resource_scope: ToolScope = ToolScope.WORKSPACE,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name=tool_id,
        description=f"Test capability for {tool_id}",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=capability,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="test",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


# Workflow 1: Feature enhancement and test verification on minimal-python repository
def test_e2e_minimal_python_enhancement(tmp_path: Path) -> None:
    repo_dir = tmp_path / "min_repo"
    create_minimal_python_repo(repo_dir)

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(repo_dir))

    # 1. Update src/calc.py to add multiply and divide functions
    calc_path = repo_dir / "src" / "calc.py"
    current_content = calc_path.read_text(encoding="utf-8")
    enhanced_content = (
        current_content
        + "\ndef multiply(a: int, b: int) -> int:\n    return a * b\n\n"
        + "def divide(a: int, b: int) -> float:\n    return a / b\n"
    )

    fs = FilesystemExecutor()
    req = ToolRequest(
        request_id=uuid4(),
        task_id=task_id,
        correlation_id=uuid4(),
        tool_id="workspace.write",
        tool_version="1.0",
        arguments={"path": "src/calc.py", "content": enhanced_content},
        requested_scope=Scope(workspace_id=uuid4(), root=str(repo_dir)),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    res = fs.execute(
        req,
        make_tool_def(
            "workspace.write",
            ToolCapability.WORKSPACE_WRITE,
            side_effects=[ToolSideEffect.WRITE],
        ),
    )
    assert res.success

    # 2. Add tests in tests/test_calc.py
    test_path = repo_dir / "tests" / "test_calc.py"
    enhanced_tests = (
        test_path.read_text(encoding="utf-8")
        + "\nfrom src.calc import multiply, divide\n\n"
        + "def test_multiply():\n    assert multiply(3, 4) == 12\n\n"
        + "def test_divide():\n    assert divide(10, 2) == 5.0\n"
    )
    req_test = ToolRequest(
        request_id=uuid4(),
        task_id=task_id,
        correlation_id=uuid4(),
        tool_id="workspace.write",
        tool_version="1.0",
        arguments={"path": "tests/test_calc.py", "content": enhanced_tests},
        requested_scope=Scope(workspace_id=uuid4(), root=str(repo_dir)),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    res_test = fs.execute(
        req_test,
        make_tool_def(
            "workspace.write",
            ToolCapability.WORKSPACE_WRITE,
            side_effects=[ToolSideEffect.WRITE],
        ),
    )
    assert res_test.success

    # 3. Execute validation runner
    runner = ValidationRunner()
    gate_def = ValidationGateDefinition(
        gate_id="unit_tests",
        command=[sys.executable, "-m", "pytest", "tests/test_calc.py"],
    )
    res_val = runner.run_gate(gate=gate_def, task_id=task_id, scope=scope)
    assert res_val.status == GateStatus.PASS

    # 4. Completion gate validates task completion
    gate = CompletionGate()
    eval_result = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["unit_tests"],
        validation_results=[res_val],
    )
    assert eval_result.can_complete is True


# Workflow 2: Multi-module repository refactor with atomic PatchEngine
def test_e2e_multi_module_patch_workflow(tmp_path: Path) -> None:
    repo_dir = tmp_path / "multi_repo"
    create_multi_module_repo(repo_dir)

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(repo_dir))

    # Apply atomic patch to sample_pkg/service.py adding delete_item
    service_path = repo_dir / "sample_pkg" / "service.py"
    current_hash = compute_file_hash(service_path)
    new_service_content = service_path.read_text(encoding="utf-8") + (
        "    def delete_item(self, item_id: str) -> bool:\n"
        "        if item_id in self._items:\n"
        "            del self._items[item_id]\n"
        "            return True\n"
        "        return False\n"
    )

    patch_engine = PatchEngine()
    patch = Patch(
        task_id=task_id,
        expected_scope=["sample_pkg/service.py"],
        file_patches=[
            FilePatch(
                path="sample_pkg/service.py",
                operation=PatchOperationType.MODIFY,
                base_hash=current_hash,
                content=new_service_content,
            )
        ],
    )
    patch_result = patch_engine.apply(patch, scope)
    assert patch_result.success is True
    assert len(patch_result.modified_files) == 1

    # Verify existing tests still pass
    runner = ValidationRunner()
    gate_def = ValidationGateDefinition(
        gate_id="service_test",
        command=[sys.executable, "-m", "pytest", "tests/test_service.py"],
    )
    res_val = runner.run_gate(gate=gate_def, task_id=task_id, scope=scope)
    assert res_val.status == GateStatus.PASS

    # Completion gate evaluation
    gate = CompletionGate()
    eval_result = gate.evaluate_completion(
        task_id=task_id,
        required_gates=["service_test"],
        validation_results=[res_val],
    )
    assert eval_result.can_complete is True


# Workflow 3: Broken build repository failure recovery workflow
def test_e2e_broken_build_recovery_workflow(tmp_path: Path) -> None:
    repo_dir = tmp_path / "broken_repo"
    create_broken_build_repo(repo_dir)

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(repo_dir))

    # 1. Run initial tests: expected to fail
    runner = ValidationRunner()
    test_gate = ValidationGateDefinition(
        gate_id="calc_test",
        command=[sys.executable, "-m", "pytest", "tests/test_broken_calc.py"],
    )
    initial_res = runner.run_gate(gate=test_gate, task_id=task_id, scope=scope)
    assert initial_res.status == GateStatus.FAIL

    # 2. Completion gate correctly blocks completion
    completion_gate = CompletionGate()
    eval_blocked = completion_gate.evaluate_completion(
        task_id=task_id,
        required_gates=["calc_test"],
        validation_results=[initial_res],
    )
    assert eval_blocked.can_complete is False

    # 3. RecoveryController detects failure and executes repair
    def fix_code() -> str:
        code_file = repo_dir / "src" / "broken_calc.py"
        code_file.write_text(
            "def compute(a: int, b: int) -> int:\n    return a + b\n",
            encoding="utf-8",
        )
        return "Fixed broken computation in broken_calc.py"

    recovery_controller = RecoveryController()
    recovery_outcome = recovery_controller.attempt_recovery(
        task_id=task_id,
        scope=scope,
        failure=initial_res,
        repair_action=fix_code,
        retest_gates=[test_gate],
    )

    assert recovery_outcome.success is True
    assert recovery_outcome.state == RecoveryState.RECOVERED
    assert len(recovery_outcome.retest_results) == 1
    assert recovery_outcome.retest_results[0].status == GateStatus.PASS

    # 4. Completion gate passes now that retest succeeded
    eval_recovered = completion_gate.evaluate_completion(
        task_id=task_id,
        required_gates=["calc_test"],
        validation_results=recovery_outcome.retest_results,
    )
    assert eval_recovered.can_complete is True
