"""Structured validation evidence and gate contracts (TVS-001 §16)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class GateStatus(StrEnum):
    """Execution status of a validation gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"
    TIMEOUT = "TIMEOUT"


class GateCategory(StrEnum):
    """Hierarchical category of validation gate (TVS-001 §17)."""

    CONTRACT = "G0_CONTRACT"
    UNIT = "G1_UNIT"
    COMPONENT = "G2_COMPONENT"
    INTEGRATION = "G3_INTEGRATION"
    SECURITY = "G4_SECURITY"
    REGRESSION = "G5_REGRESSION"
    E2E = "G6_E2E"
    PERFORMANCE = "G7_PERFORMANCE"
    ACCEPTANCE = "G8_ACCEPTANCE"
    RELEASE = "G9_RELEASE"


class ValidationResult(BaseModel):
    """Immutable evidence record representing the outcome of a validation gate."""

    model_config = ConfigDict(extra="forbid")

    result_id: UUID = Field(default_factory=uuid4)
    gate_id: str
    task_id: UUID
    command: str
    status: GateStatus
    exit_code: int | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    evidence_ref: str | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_version: str | None = None
    stdout_summary: str | None = None
    stderr_summary: str | None = None

    @property
    def is_pass(self) -> bool:
        """Return True only if this validation gate achieved a clean PASS."""
        return self.status == GateStatus.PASS
