"""Common error contracts for the AI Software Co-Agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .types import EventSeverity, Recoverability


class ErrorRecord(BaseModel):
    """Normalized error record shared across core contracts."""

    model_config = ConfigDict(extra="forbid")
    error_id: UUID
    task_id: UUID | None = None
    correlation_id: UUID
    category: str
    code: str
    source: str
    message: str
    severity: EventSeverity
    recoverability: Recoverability
    evidence_refs: list[str] = Field(default_factory=list)
    affected_scope: Any | None = None
    retry_key: str | None = None
    occurred_at: datetime
    normalized_at: datetime
