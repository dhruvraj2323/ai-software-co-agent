"""Context contracts, normalized ContextItem, and provenance (MCS-001)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from coagent.workspace.scope import WorkspaceScope


class ContextSource(StrEnum):
    """Source classification of context evidence."""

    TASK = "TASK"
    REPOSITORY = "REPOSITORY"
    SYMBOL = "SYMBOL"
    GIT = "GIT"
    VALIDATION = "VALIDATION"
    FAILURE = "FAILURE"
    PROJECT_MEMORY = "PROJECT_MEMORY"
    TASK_MEMORY = "TASK_MEMORY"
    SESSION = "SESSION"
    ARTIFACT = "ARTIFACT"
    MCP = "MCP"


class SensitivityClass(StrEnum):
    """Data sensitivity classification."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class ContextStage(StrEnum):
    """Stage in the agent lifecycle determining context ranking priorities."""

    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    IMPLEMENTATION = "IMPLEMENTATION"
    REVIEW = "REVIEW"
    VALIDATION = "VALIDATION"
    RECOVERY = "RECOVERY"
    COMPLETION = "COMPLETION"
    REPORTING = "REPORTING"


class AuthorityLayer(IntEnum):
    """Authority priority for context resolution (L0 highest, L7 lowest)."""

    L0_SECURITY = 100
    L1_TASK = 90
    L2_REPOSITORY = 80
    L3_GIT_STATE = 70
    L4_VALIDATION = 60
    L5_PROJECT_MEMORY = 40
    L6_TASK_MEMORY = 30
    L7_EXTERNAL = 10


class Provenance(BaseModel):
    """Traceability metadata for a context item (MCS-001 §9)."""

    model_config = ConfigDict(extra="forbid")

    source_type: ContextSource
    source_id: str
    source_version: str | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    derived_from: str | None = None
    locator: str | None = None
    trust_class: str = "current_evidence"
    freshness: float = 1.0


class ContextItem(BaseModel):
    """Normalized context item unit used by ranking, budgeting, and LLM assembly (MCS-001 §8)."""

    model_config = ConfigDict(extra="forbid")

    context_id: UUID = Field(default_factory=uuid4)
    source_type: ContextSource
    source_id: str
    content_or_ref: str | dict[str, Any]
    summary: str | None = None
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    freshness_score: float = Field(ge=0.0, le=1.0, default=1.0)
    authority_level: int = Field(default=int(AuthorityLayer.L2_REPOSITORY))
    provenance: Provenance
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    token_estimate: int = Field(ge=0, default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    hash: str | None = None


class ContextQuery(BaseModel):
    """Query parameters driving context selection and ranking."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    stage: ContextStage
    workspace_scope: WorkspaceScope | None = None
    target_files: list[str] = Field(default_factory=list)
    query_text: str | None = None
    max_items: int = 30

