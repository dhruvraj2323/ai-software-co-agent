"""Versioned client/runtime protocol message contracts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from coagent.core.types import EventSeverity

PROTOCOL_VERSION = "1.0"


class RequestType(StrEnum):
    """Supported client-to-runtime request types."""

    SESSION_START = "session.start"
    TASK_CREATE = "task.create"
    TASK_RESUME = "task.resume"
    TASK_PAUSE = "task.pause"
    TASK_CANCEL = "task.cancel"
    TASK_STATUS = "task.status"
    PLAN_REQUEST = "plan.request"
    APPROVAL_RESPOND = "approval.respond"
    TOOL_STATUS = "tool.status"
    VALIDATION_STATUS = "validation.status"
    COMPLETION_STATUS = "completion.status"
    WORKSPACE_REFRESH = "workspace.refresh"
    DIFF_OPEN = "diff.open"
    ARTIFACT_OPEN = "artifact.open"


class EventType(StrEnum):
    """Supported runtime-to-client event types."""

    TASK_CREATED = "task.created"
    TASK_STATE_CHANGED = "task.state_changed"
    PLAN_UPDATED = "plan.updated"
    CONTEXT_UPDATED = "context.updated"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_EXPIRED = "approval.expired"
    TOOL_STARTED = "tool.started"
    TOOL_PROGRESS = "tool.progress"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    RECOVERY_STARTED = "recovery.started"
    RECOVERY_ATTEMPT = "recovery.attempt"
    RECOVERY_EXHAUSTED = "recovery.exhausted"
    SECURITY_BLOCKED = "security.blocked"
    TASK_CANCELLED = "task.cancelled"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


class ProtocolMessage(BaseModel):
    """Base contract for versioned protocol messages."""

    model_config = ConfigDict(extra="forbid")

    protocol_version: str

    @field_validator("protocol_version")
    @classmethod
    def validate_protocol_version(cls, value: str) -> str:
        """Reject unsupported protocol versions."""
        if value != PROTOCOL_VERSION:
            raise ValueError(f"unsupported protocol version: {value}")
        return value


class ClientRequest(ProtocolMessage):
    """Validated client-to-runtime request envelope."""

    request_id: UUID
    session_id: UUID
    task_id: UUID | None = None
    type: RequestType
    payload: dict[str, Any] = Field(default_factory=dict)
    client_context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RuntimeEvent(ProtocolMessage):
    """Validated runtime-to-client event envelope."""

    event_id: UUID
    request_id: UUID | None = None
    session_id: UUID
    task_id: UUID | None = None
    type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)
    severity: EventSeverity
    created_at: datetime
