"""Unit tests for AuditRecorder and material action tracking (T088)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.artifacts.models import ArtifactReference
from coagent.audit.recorder import AuditRecorder
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


def test_audit_recorder_in_memory_recording() -> None:
    recorder = AuditRecorder()
    task_id = uuid4()
    session_id = uuid4()

    event = recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TASK_CREATED,
        payload={"goal": "Fix bug in tokenizer"},
    )

    assert recorder.count() == 1
    assert recorder.count(task_id=task_id) == 1
    assert recorder.get_events(task_id=task_id)[0] == event


def test_audit_recorder_disk_persistence_and_reload(tmp_path: Path) -> None:
    log_file = tmp_path / "audit.jsonl"
    recorder = AuditRecorder(log_path=log_file)

    task_id = uuid4()
    session_id = uuid4()

    event1 = recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TASK_CREATED,
        payload={"goal": "Initial task"},
    )
    event2 = recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="CREATED",
        to_state="PLANNING",
        reason="Started planning",
    )

    assert log_file.exists()
    assert recorder.count() == 2

    # Instantiate a second recorder pointing to the same log file to verify reload
    reloaded_recorder = AuditRecorder(log_path=log_file)
    assert reloaded_recorder.count() == 2
    events = reloaded_recorder.get_events(task_id=task_id)
    assert events[0].event_id == event1.event_id
    assert events[1].event_id == event2.event_id


def test_audit_recorder_material_action_helpers() -> None:
    recorder = AuditRecorder()
    task_id = uuid4()
    session_id = uuid4()
    scope = Scope(workspace_id=uuid4(), root="/workspace")

    # 1. Policy Decision
    req_id = uuid4()
    corr_id = uuid4()
    tool_req = ToolRequest(
        request_id=req_id,
        task_id=task_id,
        correlation_id=corr_id,
        tool_id="workspace.write_file",
        tool_version="1.0.0",
        arguments={"path": "src/main.py", "content": "print('hello')"},
        requested_scope=scope,
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    decision = PolicyDecision(
        request_id=tool_req.request_id,
        task_id=task_id,
        correlation_id=tool_req.correlation_id,
        outcome=PolicyDecisionOutcome.ALLOW,
        reason="Authorized workspace mutation",
        rule_id="RULE_ALLOW_WORKSPACE_WRITE",
        evaluated_scope=scope,
        risk_level=ToolRiskLevel.LOW,
        created_at=datetime.now(UTC),
    )
    pol_event = recorder.record_policy_decision(
        task_id=task_id,
        session_id=session_id,
        decision=decision,
        request=tool_req,
        definition=None,
    )
    assert pol_event.type == EventType.POLICY_DECISION.value
    assert pol_event.payload["tool_id"] == "workspace.write_file"

    # 2. Tool Execution
    result = ToolResult(
        request_id=tool_req.request_id,
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"bytes_written": 14},
        scope_effect=ScopeEffect.MODIFIED,
        created_at=datetime.now(UTC),
    )
    exec_event = recorder.record_tool_execution(
        task_id=task_id,
        session_id=session_id,
        request=tool_req,
        result=result,
    )
    assert exec_event.type == EventType.TOOL_EXECUTED.value
    assert exec_event.payload["success"] is True

    # 3. Validation
    val_res = ValidationResult(
        gate_id="unit_tests",
        task_id=task_id,
        command="pytest",
        status=GateStatus.PASS,
        exit_code=0,
    )
    val_event = recorder.record_validation(
        task_id=task_id,
        session_id=session_id,
        result=val_res,
    )
    assert val_event.type == EventType.VALIDATION_COMPLETED.value
    assert val_event.payload["status"] == "PASS"

    # 4. Artifact Reference
    art_ref = ArtifactReference(
        task_id=task_id,
        name="evidence.log",
        media_type="text/plain",
        sha256_hash="abc123hash",
        size_bytes=42,
        storage_path="evidence.log",
    )
    art_event = recorder.record_artifact(
        task_id=task_id,
        session_id=session_id,
        reference=art_ref,
    )
    assert art_event.type == EventType.ARTIFACT_STORED.value


def test_audit_recorder_auto_redacts_secrets() -> None:
    recorder = AuditRecorder()
    task_id = uuid4()
    session_id = uuid4()

    fake_token = "ghp_" + "SECRET1234567890ABCDEF"

    event = recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TOOL_EXECUTED,
        payload={"sensitive_command": f"export TOKEN={fake_token}"},
    )

    assert fake_token not in str(event.payload)
    assert "[REDACTED]" in str(event.payload)
