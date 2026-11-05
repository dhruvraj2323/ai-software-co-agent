"""Unit tests for ValidationRunner and ValidationResult evidence models (T076, T077)."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

from coagent.validation.evidence import GateCategory, GateStatus
from coagent.validation.runner import ValidationGateDefinition, ValidationRunner
from coagent.workspace.scope import WorkspaceScope


def test_validation_runner_executes_passing_gate(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    runner = ValidationRunner()

    gate = ValidationGateDefinition(
        gate_id="unit_tests",
        command=[sys.executable, "-c", "import sys; sys.exit(0)"],
        category=GateCategory.UNIT,
    )

    result = runner.run_gate(gate, task_id=scope.task_id, scope=scope, source_version="v1_abc")

    assert result.status == GateStatus.PASS
    assert result.is_pass is True
    assert result.exit_code == 0
    assert result.source_version == "v1_abc"
    assert result.duration_ms is not None and result.duration_ms >= 0


def test_validation_runner_detects_failing_gate(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    scope = WorkspaceScope(task_id=uuid4(), workspace_id=uuid4(), root=str(workspace_dir))
    runner = ValidationRunner()

    gate = ValidationGateDefinition(
        gate_id="lint_check",
        command=[sys.executable, "-c", "import sys; sys.stderr.write('Syntax error'); sys.exit(1)"],
        category=GateCategory.CONTRACT,
    )

    result = runner.run_gate(gate, task_id=scope.task_id, scope=scope)

    assert result.status == GateStatus.FAIL
    assert result.is_pass is False
    assert result.exit_code == 1
    assert "Syntax error" in (result.stderr_summary or "")
