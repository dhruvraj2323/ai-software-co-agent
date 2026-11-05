"""Unit tests for TaskTrace and TaskTraceReconstructor (T091)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from coagent.artifacts.models import ArtifactReference
from coagent.audit.recorder import AuditRecorder
from coagent.audit.trace import TaskTraceReconstructor
from coagent.core.events import EventType
from coagent.policy.contracts import PolicyDecision, PolicyDecisionOutcome
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ScopeEffect,
    ToolRequest,
    ToolRequestSource,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.registry import ToolRiskLevel
from coagent.validation.evidence import GateStatus, ValidationResult


def test_task_trace_reconstruction_complete_lifecycle() -> None:
    recorder = AuditRecorder()
    reconstructor = TaskTraceReconstructor(recorder)

    task_id = uuid4()
    session_id = uuid4()
    scope = Scope(workspace_id=uuid4(), root="/workspace")

    # 1. Created
    recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TASK_CREATED,
        payload={"goal": "Refactor auth middleware"},
    )

    # 2. State: PLANNING
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="CREATED",
        to_state="PLANNING",
        reason="Generating plan",
    )

    # 3. Tool Policy & Execution
    req_id = uuid4()
    corr_id = uuid4()
    req = ToolRequest(
        request_id=req_id,
        task_id=task_id,
        correlation_id=corr_id,
        tool_id="workspace.read_file",
        tool_version="1.0.0",
        arguments={"path": "auth.py"},
        requested_scope=scope,
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    decision = PolicyDecision(
        request_id=req.request_id,
        task_id=task_id,
        correlation_id=req.correlation_id,
        outcome=PolicyDecisionOutcome.ALLOW,
        reason="Authorized read",
        rule_id="RULE_ALLOW_READ",
        evaluated_scope=scope,
        risk_level=ToolRiskLevel.LOW,
        created_at=datetime.now(UTC),
    )
    recorder.record_policy_decision(
        task_id=task_id,
        session_id=session_id,
        decision=decision,
        request=req,
    )
    res = ToolResult(
        request_id=req.request_id,
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"content": "def authenticate(): pass"},
        scope_effect=ScopeEffect.NONE,
        created_at=datetime.now(UTC),
    )
    recorder.record_tool_execution(
        task_id=task_id,
        session_id=session_id,
        request=req,
        result=res,
    )

    # 4. State: VALIDATING & Validation Result
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="IMPLEMENTING",
        to_state="VALIDATING",
    )
    val_res = ValidationResult(
        gate_id="unit_gate",
        task_id=task_id,
        command="pytest",
        status=GateStatus.PASS,
        exit_code=0,
    )
    recorder.record_validation(
        task_id=task_id,
        session_id=session_id,
        result=val_res,
    )

    # 5. Artifact Stored
    art = ArtifactReference(
        task_id=task_id,
        name="pytest_stdout.log",
        media_type="text/plain",
        sha256_hash="deadbeef1234",
        size_bytes=100,
        storage_path="artifacts/pytest_stdout.log",
    )
    recorder.record_artifact(
        task_id=task_id,
        session_id=session_id,
        reference=art,
    )

    # 6. State: COMPLETE
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="VALIDATING",
        to_state="COMPLETE",
        reason="All validation gates passed cleanly",
    )

    # Reconstruct trace
    trace = reconstructor.reconstruct(task_id)

    assert trace.is_reconstructable is True
    assert trace.task_id == task_id
    assert trace.session_id == session_id
    assert trace.initial_goal == "Refactor auth middleware"
    assert trace.final_state == "COMPLETE"
    assert trace.is_complete is True
    assert len(trace.lifecycle_states) == 3
    assert len(trace.policy_decisions) == 1
    assert len(trace.tool_executions) == 1
    assert len(trace.validations) == 1
    assert len(trace.artifacts) == 1
    assert trace.artifacts[0].name == "pytest_stdout.log"

    summary_text = trace.summary()
    assert "Refactor auth middleware" in summary_text
    assert "**Final State**: COMPLETE" in summary_text


def test_task_trace_empty_for_unknown_task() -> None:
    recorder = AuditRecorder()
    reconstructor = TaskTraceReconstructor(recorder)
    unknown_id = uuid4()

    trace = reconstructor.reconstruct(unknown_id)
    assert trace.is_reconstructable is False
    assert trace.task_id == unknown_id
    assert trace.final_state == "UNKNOWN"
