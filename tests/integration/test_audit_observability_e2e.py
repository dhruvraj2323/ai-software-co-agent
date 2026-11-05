"""End-to-end integration test for audit, artifacts, and observability (T092)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.artifacts.store import ArtifactStore
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


def test_audit_observability_e2e_reconstruction(tmp_path: Path) -> None:
    # 1. Setup workspace, audit log, and artifact store
    audit_file = tmp_path / "audit_log.jsonl"
    artifact_root = tmp_path / "artifacts"

    recorder = AuditRecorder(log_path=audit_file)
    store = ArtifactStore(artifact_root)

    task_id = uuid4()
    session_id = uuid4()
    correlation_id = uuid4()
    scope = Scope(workspace_id=uuid4(), root=str(tmp_path / "workspace"))

    # 2. TASK_CREATED
    recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TASK_CREATED,
        payload={"goal": "Refactor repository search indexer", "files": ["src/search.py"]},
        correlation_id=correlation_id,
    )

    # 3. State -> PLANNING
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="CREATED",
        to_state="PLANNING",
        correlation_id=correlation_id,
    )

    # 4. State -> IMPLEMENTING
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="PLANNING",
        to_state="IMPLEMENTING",
        correlation_id=correlation_id,
    )

    # 5. Tool evaluation & execution
    req_id = uuid4()
    tool_req = ToolRequest(
        request_id=req_id,
        task_id=task_id,
        correlation_id=correlation_id,
        tool_id="workspace.write_file",
        tool_version="1.0.0",
        arguments={"path": "src/search.py", "content": "class SearchIndex: pass"},
        requested_scope=scope,
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    pol_dec = PolicyDecision(
        request_id=tool_req.request_id,
        task_id=task_id,
        correlation_id=correlation_id,
        outcome=PolicyDecisionOutcome.ALLOW,
        reason="Approved workspace mutation",
        rule_id="RULE_ALLOW_WORKSPACE_WRITE",
        evaluated_scope=scope,
        risk_level=ToolRiskLevel.LOW,
        created_at=datetime.now(UTC),
    )
    recorder.record_policy_decision(
        task_id=task_id,
        session_id=session_id,
        decision=pol_dec,
        request=tool_req,
        correlation_id=correlation_id,
    )

    tool_res = ToolResult(
        request_id=tool_req.request_id,
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"bytes_written": 25},
        scope_effect=ScopeEffect.MODIFIED,
        created_at=datetime.now(UTC),
    )
    recorder.record_tool_execution(
        task_id=task_id,
        session_id=session_id,
        request=tool_req,
        result=tool_res,
        correlation_id=correlation_id,
    )

    # 6. Large test output stored in ArtifactStore and recorded
    large_stdout = "Test Suite Run:\n" + ("PASSED test_case\n" * 50)
    art_ref = store.store_text(
        task_id=task_id,
        name="pytest_stdout.log",
        content=large_stdout,
        media_type="text/plain",
        metadata={"stage": "validation_gate"},
    )
    recorder.record_artifact(
        task_id=task_id,
        session_id=session_id,
        reference=art_ref,
        correlation_id=correlation_id,
    )

    # 7. State -> VALIDATING & Validation Result
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="IMPLEMENTING",
        to_state="VALIDATING",
        correlation_id=correlation_id,
    )
    val_res = ValidationResult(
        gate_id="unit_tests",
        task_id=task_id,
        command="pytest tests/unit",
        status=GateStatus.PASS,
        exit_code=0,
        duration_ms=450,
    )
    recorder.record_validation(
        task_id=task_id,
        session_id=session_id,
        result=val_res,
        correlation_id=correlation_id,
    )

    # 8. State -> COMPLETE
    recorder.record_state_transition(
        task_id=task_id,
        session_id=session_id,
        from_state="VALIDATING",
        to_state="COMPLETE",
        reason="Validation gate passed",
        correlation_id=correlation_id,
    )

    # 9. Verify correlation across all events
    events = recorder.get_events(task_id=task_id)
    assert len(events) == 9
    for ev in events:
        assert ev.task_id == task_id
        assert ev.session_id == session_id
        assert ev.correlation_id == correlation_id

    # 10. Reconstruct timeline and verify full fidelity
    reconstructor = TaskTraceReconstructor(recorder)
    trace = reconstructor.reconstruct(task_id)

    assert trace.is_reconstructable is True
    assert trace.is_complete is True
    assert trace.final_state == "COMPLETE"
    assert trace.initial_goal == "Refactor repository search indexer"
    assert len(trace.lifecycle_states) == 4
    assert len(trace.policy_decisions) == 1
    assert len(trace.tool_executions) == 1
    assert len(trace.artifacts) == 1
    assert len(trace.validations) == 1

    # Verify retrieved artifact from store matches stored content
    recovered_artifact = trace.artifacts[0]
    retrieved_content = store.retrieve_text(recovered_artifact)
    assert retrieved_content == large_stdout
