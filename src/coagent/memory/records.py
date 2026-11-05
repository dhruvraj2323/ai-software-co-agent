"""Typed memory record contracts, types, and statuses (MCS-001 §6, §7)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from coagent.context.contracts import Provenance, SensitivityClass


class MemoryType(StrEnum):
    """Classification of persistent memory records."""

    TASK_STATE = "TASK_STATE"
    TASK_MEMORY = "TASK_MEMORY"
    PROJECT_MEMORY = "PROJECT_MEMORY"
    DECISION_MEMORY = "DECISION_MEMORY"
    FAILURE_MEMORY = "FAILURE_MEMORY"
    SESSION_MEMORY = "SESSION_MEMORY"


class MemoryStatus(StrEnum):
    """Lifecycle and validity state of a memory record."""

    ACTIVE = "ACTIVE"
    STALE = "STALE"
    INVALID = "INVALID"
    ARCHIVED = "ARCHIVED"


class MemorySource(StrEnum):
    """Source origin of a memory record."""

    USER = "USER"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"
    OBSERVATION = "OBSERVATION"
    VALIDATION = "VALIDATION"


class MemoryRecord(BaseModel):
    """Structured, versioned, provenance-tracked memory record (MCS-001 §7)."""

    model_config = ConfigDict(extra="forbid")

    memory_id: UUID = Field(default_factory=uuid4)
    type: MemoryType
    project_id: UUID | None = None
    task_id: UUID | None = None
    key: str = Field(min_length=1)
    value: dict[str, Any] | list[Any] | str | int | float | bool
    summary: str | None = None
    source: MemorySource
    provenance: Provenance
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    version: int = Field(default=1, ge=1)
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    status: MemoryStatus = MemoryStatus.ACTIVE

