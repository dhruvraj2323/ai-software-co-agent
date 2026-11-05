"""Authoritative audit recorder with correlation metadata and redaction (T088, REQ-092)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from coagent.artifacts.models import ArtifactReference
from coagent.audit.redaction import OutputRedactor
from coagent.core.events import EventEnvelope, EventType
from coagent.core.types import EventSeverity
from coagent.policy.contracts import PolicyDecision
from coagent.tools.contracts import ToolRequest, ToolResult
from coagent.tools.registry import ToolDefinition
from coagent.validation.evidence import ValidationResult


class AuditRecorder:
    """Thread-safe, append-only recorder for material events, policy decisions, and evidence."""

    def __init__(
        self,
        log_path: Path | str | None = None,
        redactor: OutputRedactor | None = None,
        auto_redact: bool = True,
    ) -> None:
        self._events: list[EventEnvelope] = []
        self._log_path = Path(log_path).resolve() if log_path else None
        self._redactor = redactor or OutputRedactor()
        self._auto_redact = auto_redact

        if self._log_path:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            if self._log_path.exists():
                self.load_from_disk()

    @property
    def log_path(self) -> Path | None:
        """Path to the append-only audit JSONL file on disk."""
        return self._log_path

    def load_from_disk(self) -> None:
        """Load and parse historical event envelopes from the JSONL log file."""
        if not self._log_path or not self._log_path.exists():
            return

        with self._log_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    try:
                        data = json.loads(stripped)
                        envelope = EventEnvelope.model_validate(data)
                        self._events.append(envelope)
                    except Exception:
                        continue

    def record_event(self, event: EventEnvelope) -> EventEnvelope:
        """Record an event envelope into the audit trail, applying redaction."""
        stored = self._redactor.redact_event(event) if self._auto_redact else event
        self._events.append(stored)

        if self._log_path:
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(stored.model_dump_json() + "\n")

        return stored

    def record_task_event(
        self,
        *,
        task_id: UUID,
        session_id: UUID,
        event_type: str | EventType,
        payload: Any,
        request_id: UUID | None = None,
        correlation_id: UUID | None = None,
        severity: EventSeverity = EventSeverity.INFO,
        source: str = "runtime",
    ) -> EventEnvelope:
        """Create and record a structured event envelope."""
        envelope = EventEnvelope.create(
            event_type=event_type,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            request_id=request_id,
            correlation_id=correlation_id,
            severity=severity,
            source=source,
        )
        return self.record_event(envelope)

    def record_policy_decision(
        self,
        task_id: UUID,
        session_id: UUID,
        decision: PolicyDecision,
        request: ToolRequest,
        definition: ToolDefinition | None = None,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record a material tool policy evaluation decision (T039)."""
        outcome = decision.outcome
        outcome_val = outcome.value if hasattr(outcome, "value") else str(outcome)
        risk = decision.risk_level
        risk_val = risk.value if hasattr(risk, "value") else str(risk)

        payload = {
            "request_id": str(request.request_id),
            "tool_id": request.tool_id,
            "decision": outcome_val,
            "policy_rule": decision.rule_id,
            "reason": decision.reason,
            "risk_level": risk_val,
            "arguments": request.arguments,
        }
        if definition:
            payload["tool_description"] = definition.description

        envelope = EventEnvelope.create(
            event_type=EventType.POLICY_DECISION,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            request_id=request.request_id,
            correlation_id=correlation_id or request.correlation_id,
            severity=EventSeverity.INFO,
            source="policy_evaluator",
        )
        return self.record_event(envelope)

    def record_tool_execution(
        self,
        task_id: UUID,
        session_id: UUID,
        request: ToolRequest,
        result: ToolResult,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record an authorized tool execution result."""
        payload = {
            "request_id": str(request.request_id),
            "tool_id": request.tool_id,
            "status": result.status.value,
            "success": result.success,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms,
            "output": result.output,
            "error": result.error.model_dump() if result.error else None,
        }
        envelope = EventEnvelope.create(
            event_type=EventType.TOOL_EXECUTED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            request_id=request.request_id,
            correlation_id=correlation_id or request.correlation_id,
            severity=EventSeverity.INFO if result.success else EventSeverity.ERROR,
            source="tool_gateway",
        )
        return self.record_event(envelope)

    def record_state_transition(
        self,
        task_id: UUID,
        session_id: UUID,
        from_state: str,
        to_state: str,
        reason: str | None = None,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record a task lifecycle state transition."""
        payload = {
            "from_state": from_state,
            "to_state": to_state,
            "reason": reason,
        }
        envelope = EventEnvelope.create(
            event_type=EventType.TASK_STATE_CHANGED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=EventSeverity.INFO,
            source="task_state_machine",
        )
        return self.record_event(envelope)

    def record_validation(
        self,
        task_id: UUID,
        session_id: UUID,
        result: ValidationResult,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record a validation gate execution result."""
        payload = result.model_dump()
        envelope = EventEnvelope.create(
            event_type=EventType.VALIDATION_COMPLETED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=EventSeverity.INFO if result.is_pass else EventSeverity.ERROR,
            source="validation_runner",
        )
        return self.record_event(envelope)

    def record_approval(
        self,
        task_id: UUID,
        session_id: UUID,
        approval_id: UUID,
        granted: bool,
        decided_by: str,
        reason: str | None = None,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record a user or automated approval resolution."""
        payload = {
            "approval_id": str(approval_id),
            "granted": granted,
            "decided_by": decided_by,
            "reason": reason,
        }
        envelope = EventEnvelope.create(
            event_type=EventType.APPROVAL_RESOLVED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=EventSeverity.INFO if granted else EventSeverity.WARNING,
            source="approval_manager",
        )
        return self.record_event(envelope)

    def record_patch(
        self,
        task_id: UUID,
        session_id: UUID,
        patch_id: str,
        files: list[str],
        success: bool,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record an atomic patch application attempt."""
        payload = {
            "patch_id": patch_id,
            "files": files,
            "success": success,
        }
        envelope = EventEnvelope.create(
            event_type=EventType.PATCH_APPLIED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=EventSeverity.INFO if success else EventSeverity.ERROR,
            source="patch_engine",
        )
        return self.record_event(envelope)

    def record_artifact(
        self,
        task_id: UUID,
        session_id: UUID,
        reference: ArtifactReference,
        correlation_id: UUID | None = None,
    ) -> EventEnvelope:
        """Record the creation and storage of an offloaded evidence artifact."""
        payload = reference.model_dump()
        envelope = EventEnvelope.create(
            event_type=EventType.ARTIFACT_STORED,
            task_id=task_id,
            session_id=session_id,
            payload=payload,
            correlation_id=correlation_id,
            severity=EventSeverity.INFO,
            source="artifact_store",
        )
        return self.record_event(envelope)

    def get_events(
        self,
        task_id: UUID | None = None,
        event_type: str | EventType | None = None,
        correlation_id: UUID | None = None,
        since: datetime | None = None,
    ) -> list[EventEnvelope]:
        """Query recorded events with optional filtering criteria."""
        type_str = event_type.value if isinstance(event_type, EventType) else (
            str(event_type) if event_type is not None else None
        )

        matched: list[EventEnvelope] = []
        for event in self._events:
            if task_id and event.task_id != task_id:
                continue
            if type_str and event.type != type_str:
                continue
            if correlation_id and event.correlation_id != correlation_id:
                continue
            if since and event.timestamp < since:
                continue
            matched.append(event)
        return matched

    def get_correlated_events(self, correlation_id: UUID) -> list[EventEnvelope]:
        """Retrieve all events sharing the given correlation identifier."""
        return self.get_events(correlation_id=correlation_id)

    def count(self, task_id: UUID | None = None) -> int:
        """Return the count of recorded events."""
        if task_id is None:
            return len(self._events)
        return sum(1 for e in self._events if e.task_id == task_id)

    def clear(self) -> None:
        """Clear in-memory events and truncate log file if configured."""
        self._events.clear()
        if self._log_path and self._log_path.exists():
            self._log_path.write_text("", encoding="utf-8")
