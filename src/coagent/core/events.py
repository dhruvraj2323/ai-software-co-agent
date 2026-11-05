"""Common event envelope contract for the AI Software Co-Agent (T012, T087)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .types import EventSeverity


class EventType(StrEnum):
    """Canonical runtime event types (T087)."""

    TASK_CREATED = "TASK_CREATED"
    TASK_STATE_CHANGED = "TASK_STATE_CHANGED"
    PLAN_UPDATED = "PLAN_UPDATED"
    TOOL_REQUESTED = "TOOL_REQUESTED"
    POLICY_DECISION = "POLICY_DECISION"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    PATCH_APPLIED = "PATCH_APPLIED"
    VALIDATION_STARTED = "VALIDATION_STARTED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    RECOVERY_STARTED = "RECOVERY_STARTED"
    RECOVERY_COMPLETED = "RECOVERY_COMPLETED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_RESOLVED = "APPROVAL_RESOLVED"
    ARTIFACT_STORED = "ARTIFACT_STORED"
    GENERIC = "GENERIC"


class EventEnvelope(BaseModel):
    """Common event envelope used for correlated runtime events (T087)."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    session_id: UUID
    task_id: UUID
    type: str
    severity: EventSeverity
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str
    payload: Any
    correlation_id: UUID | None = None

    @classmethod
    def create(
        cls,
        *,
        event_type: str | EventType,
        task_id: UUID,
        session_id: UUID,
        payload: Any,
        request_id: UUID | None = None,
        correlation_id: UUID | None = None,
        severity: EventSeverity = EventSeverity.INFO,
        source: str = "runtime",
        timestamp: datetime | None = None,
    ) -> EventEnvelope:
        """Convenience factory method to instantiate a correlated event envelope."""
        actual_req_id = request_id or uuid4()
        actual_corr_id = correlation_id or actual_req_id
        type_str = event_type.value if isinstance(event_type, EventType) else str(event_type)

        return cls(
            event_id=uuid4(),
            request_id=actual_req_id,
            session_id=session_id,
            task_id=task_id,
            type=type_str,
            severity=severity,
            timestamp=timestamp or datetime.now(UTC),
            source=source,
            payload=payload,
            correlation_id=actual_corr_id,
        )
