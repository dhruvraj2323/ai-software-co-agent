"""Artifact reference and evidence metadata models (T089)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ArtifactReference(BaseModel):
    """Immutable reference to an offloaded large evidence artifact (T089)."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    name: str
    media_type: str = "text/plain"
    sha256_hash: str
    size_bytes: int = Field(ge=0)
    storage_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
