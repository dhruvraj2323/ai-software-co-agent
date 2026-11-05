"""Context manifest and provenance audit record (MCS-001 §22)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SelectedItemRecord(BaseModel):
    """Metadata record of an included context item."""

    model_config = ConfigDict(extra="forbid")

    context_id: UUID
    source_id: str
    source_version: str | None = None
    relevance: float
    freshness: float
    token_estimate: int
    composite_score: float


class OmittedItemRecord(BaseModel):
    """Audit record of an item excluded during ranking or budgeting."""

    model_config = ConfigDict(extra="forbid")

    context_id: UUID | None = None
    source_id: str
    source_type: str
    reason: str
    token_estimate: int


class RedactionRecord(BaseModel):
    """Audit evidence that sensitive information was masked prior to model delivery."""

    model_config = ConfigDict(extra="forbid")

    context_id: UUID
    redaction_type: str
    reason: str


class ContextManifest(BaseModel):
    """Explainable manifest of all included, omitted, and redacted context items."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    stage: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context_budget: int
    total_tokens: int
    selected_items: list[SelectedItemRecord]
    omitted_items: list[OmittedItemRecord] = Field(default_factory=list)
    redactions: list[RedactionRecord] = Field(default_factory=list)
    assembly_version: str = "v1.0"

