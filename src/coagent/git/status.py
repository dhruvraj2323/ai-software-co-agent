"""Structured Git status contracts (T045)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GitStatus(BaseModel):
    """Normalized repository Git status."""

    model_config = ConfigDict(extra="forbid")
    branch: str = Field(default="HEAD")
    commit_hash: str | None = None
    is_clean: bool = True
    staged_files: list[str] = Field(default_factory=list)
    modified_files: list[str] = Field(default_factory=list)
    untracked_files: list[str] = Field(default_factory=list)

    @property
    def has_uncommitted_changes(self) -> bool:
        """Return True if any staged or modified files exist."""
        return bool(self.staged_files or self.modified_files)
