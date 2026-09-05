"""Canonical task-authorized workspace scope contract."""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceScope(BaseModel):
    """Explicit workspace boundary associated with an owning task.
    This model represents the declared workspace scope only. Filesystem
    canonicalization and security enforcement are intentionally deferred
    to later security/workspace tasks.
    """
    model_config = ConfigDict(extra="forbid")
    task_id: UUID = Field(description="Task authorized to use this workspace scope.")
    workspace_id: UUID = Field(description="Stable identity of the workspace.")
    root: str = Field(min_length=1, description="Declared workspace root.")
