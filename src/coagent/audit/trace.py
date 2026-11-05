"""Task trace reconstruction and timeline visualization (T091, MA-A11)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.artifacts.models import ArtifactReference
from coagent.audit.recorder import AuditRecorder
from coagent.core.events import EventEnvelope, EventType
from coagent.core.types import EventSeverity


class StateTransitionRecord(BaseModel):
    """Reconstructed record of a task lifecycle transition."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    from_state: str
    to_state: str
    reason: str | None = None


class ToolExecutionRecord(BaseModel):
    """Reconstructed record of an authorized tool call."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    request_id: str
    tool_id: str
    status: str
    success: bool
    exit_code: int | None = None
    duration_ms: int | None = 0
    output: Any = None
    error: Any = None


class PolicyDecisionRecord(BaseModel):
    """Reconstructed record of a tool policy evaluation."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    tool_id: str
    decision: str
    rule_id: str | None = None
    reason: str
    requires_approval: bool = False


class TaskTrace(BaseModel):
    """Authoritative, reconstructed timeline of an entire task lifecycle (T091)."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    session_id: UUID | None = None
    correlation_id: UUID | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    total_duration_ms: int = 0
    initial_goal: str | None = None
    final_state: str = "UNKNOWN"
    is_complete: bool = False
    is_reconstructable: bool = True
    lifecycle_states: list[StateTransitionRecord] = Field(default_factory=list)
    policy_decisions: list[PolicyDecisionRecord] = Field(default_factory=list)
    tool_executions: list[ToolExecutionRecord] = Field(default_factory=list)
    validations: list[dict[str, Any]] = Field(default_factory=list)
    approvals: list[dict[str, Any]] = Field(default_factory=list)
    patches: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[ArtifactReference] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)

    def summary(self) -> str:
        """Produce a structured, human-readable summary of the reconstructed task."""
        lines = [
            f"# Task Trace Summary: {self.task_id}",
            f"- **Session ID**: {self.session_id}",
            f"- **Final State**: {self.final_state}",
            f"- **Is Complete**: {self.is_complete}",
            f"- **Total Duration**: {self.total_duration_ms} ms",
            f"- **State Transitions**: {len(self.lifecycle_states)}",
            f"- **Tool Executions**: {len(self.tool_executions)}",
            f"- **Policy Decisions**: {len(self.policy_decisions)}",
            f"- **Validation Gates**: {len(self.validations)}",
            f"- **Artifacts Stored**: {len(self.artifacts)}",
            f"- **Errors Encountered**: {len(self.errors)}",
        ]
        if self.initial_goal:
            lines.insert(1, f"- **Goal**: {self.initial_goal}")
        return "\n".join(lines)


class TaskTraceReconstructor:
    """Reconstructs the authoritative task timeline from event streams or an audit recorder."""

    def __init__(self, recorder: AuditRecorder | None = None) -> None:
        self._recorder = recorder

    def reconstruct(
        self,
        task_id: UUID,
        events: list[EventEnvelope] | None = None,
    ) -> TaskTrace:
        """Parse audit event envelopes into a chronologically ordered TaskTrace."""
        raw_events: list[EventEnvelope] = []
        if events is not None:
            raw_events = [e for e in events if e.task_id == task_id]
        elif self._recorder is not None:
            raw_events = self._recorder.get_events(task_id=task_id)

        if not raw_events:
            return TaskTrace(
                task_id=task_id,
                is_reconstructable=False,
                final_state="UNKNOWN",
            )

        # Sort events chronologically
        sorted_events = sorted(raw_events, key=lambda e: e.timestamp)

        trace = TaskTrace(
            task_id=task_id,
            session_id=sorted_events[0].session_id,
            correlation_id=sorted_events[0].correlation_id,
            created_at=sorted_events[0].timestamp,
            final_state="UNKNOWN",
        )

        for event in sorted_events:
            payload = event.payload if isinstance(event.payload, dict) else {}

            if event.type == EventType.TASK_CREATED.value:
                trace.initial_goal = payload.get("goal") or payload.get("description")

            elif event.type == EventType.TASK_STATE_CHANGED.value:
                to_state = payload.get("to_state", "UNKNOWN")
                from_state = payload.get("from_state", "UNKNOWN")
                reason = payload.get("reason")
                trace.lifecycle_states.append(
                    StateTransitionRecord(
                        timestamp=event.timestamp,
                        from_state=from_state,
                        to_state=to_state,
                        reason=reason,
                    )
                )
                trace.final_state = to_state
                if to_state == "COMPLETE":
                    trace.is_complete = True
                    trace.completed_at = event.timestamp

            elif event.type == EventType.POLICY_DECISION.value:
                trace.policy_decisions.append(
                    PolicyDecisionRecord(
                        timestamp=event.timestamp,
                        tool_id=payload.get("tool_id", "unknown"),
                        decision=payload.get("decision", "DENY"),
                        rule_id=payload.get("policy_rule"),
                        reason=payload.get("reason", ""),
                        requires_approval=payload.get("requires_approval", False),
                    )
                )

            elif event.type == EventType.TOOL_EXECUTED.value:
                dur = payload.get("duration_ms")
                actual_duration = dur if isinstance(dur, int) else 0
                trace.tool_executions.append(
                    ToolExecutionRecord(
                        timestamp=event.timestamp,
                        request_id=payload.get("request_id", str(event.request_id)),
                        tool_id=payload.get("tool_id", "unknown"),
                        status=payload.get("status", "UNKNOWN"),
                        success=payload.get("success", False),
                        exit_code=payload.get("exit_code"),
                        duration_ms=actual_duration,
                        output=payload.get("output"),
                        error=payload.get("error"),
                    )
                )

            elif event.type == EventType.VALIDATION_COMPLETED.value:
                trace.validations.append(payload)

            elif event.type == EventType.APPROVAL_RESOLVED.value:
                trace.approvals.append(payload)

            elif event.type == EventType.PATCH_APPLIED.value:
                trace.patches.append(payload)

            elif event.type == EventType.ARTIFACT_STORED.value:
                try:
                    ref = ArtifactReference.model_validate(payload)
                    trace.artifacts.append(ref)
                except Exception:
                    pass

            if event.severity in (EventSeverity.ERROR, EventSeverity.CRITICAL):
                trace.errors.append({
                    "event_id": str(event.event_id),
                    "type": event.type,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "payload": payload,
                })

        last_time = trace.completed_at or sorted_events[-1].timestamp
        if trace.created_at:
            delta = (last_time - trace.created_at).total_seconds()
            trace.total_duration_ms = max(0, int(delta * 1000))

        return trace
