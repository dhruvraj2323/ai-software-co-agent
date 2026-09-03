"""Common result contracts for the AI Software Co-Agent."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .errors import ErrorRecord


class Result[T](BaseModel):
    """Typed success/failure result envelope."""

    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    success: bool
    result: T | None = None
    error: ErrorRecord | None = None

    def model_post_init(self, __context: object) -> None:
        """Validate success/error/result consistency."""
        if self.success:
            if self.error is not None:
                raise ValueError("successful results cannot contain an error")
            if self.result is None:
                raise ValueError("successful results must contain a result")
        else:
            if self.error is None:
                raise ValueError("failed results must contain an error")
            if self.result is not None:
                raise ValueError("failed results cannot contain a result")
