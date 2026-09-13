"""Canonical tool request and result contracts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from coagent.core.errors import ErrorRecord


class ToolResultStatus(StrEnum):
    """Normalized execution status for a tool result."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    DENIED = "DENIED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class ToolRequestSource(StrEnum):
    """Authoritative origin categories for tool requests."""

    AGENT = "Agent"
    RECOVERY = "Recovery"
    USER = "User"


class AutonomyMode(StrEnum):
    """Supported autonomy modes defined by the tool permission baseline."""

    CHAT = "CHAT"
    PLAN = "PLAN"
    ASSISTED_IMPLEMENT = "ASSISTED IMPLEMENT"
    SUPERVISED_AUTO = "SUPERVISED AUTO"
    AUTONOMOUS = "AUTONOMOUS"
    RESTRICTED = "RESTRICTED"


class Scope(BaseModel):
    """Canonical typed resource scope carried by a tool request."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    workspace_id: UUID
    root: str = Field(min_length=1)


class ScopeEffect(StrEnum):
    """Normalized effect of a tool operation on its requested scope."""

    NONE = "NONE"
    UNCHANGED = "UNCHANGED"
    NARROWED = "NARROWED"
    MODIFIED = "MODIFIED"


class ToolRequest(BaseModel):
    """Canonical typed request submitted to the tool authorization path."""

    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    task_id: UUID
    correlation_id: UUID
    tool_id: str = Field(min_length=1)
    tool_version: str = Field(min_length=1)
    arguments: dict[str, Any]
    requested_scope: Scope
    autonomy_mode: AutonomyMode
    source: ToolRequestSource
    created_at: datetime


class ToolResult(BaseModel):
    """Canonical normalized result returned by a tool executor."""

    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    success: bool
    status: ToolResultStatus
    output: dict[str, Any] | None = None
    error: ErrorRecord | None = None
    exit_code: int | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    evidence_ref: str | None = None
    scope_effect: ScopeEffect
    created_at: datetime

    @model_validator(mode="after")
    def validate_consistency(self) -> ToolResult:
        """Ensure success/status/output/error remain internally consistent."""
        if self.success:
            if self.status is not ToolResultStatus.SUCCESS:
                raise ValueError("successful tool results must have SUCCESS status")
            if self.output is None:
                raise ValueError("successful tool results must contain output")
            if self.error is not None:
                raise ValueError("successful tool results cannot contain an error")
        else:
            if self.status is ToolResultStatus.SUCCESS:
                raise ValueError("failed tool results cannot have SUCCESS status")
            if self.error is None:
                raise ValueError("failed tool results must contain an error")
            if self.output is not None:
                raise ValueError("failed tool results cannot contain output")
        return self
