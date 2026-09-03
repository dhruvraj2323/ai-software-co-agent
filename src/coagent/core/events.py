"""Common event envelope contract for the AI Software Co-Agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .types import EventSeverity


class EventEnvelope(BaseModel):
    """Common event envelope used for correlated runtime events."""

    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    request_id: UUID
    session_id: UUID
    task_id: UUID
    type: str
    severity: EventSeverity
    timestamp: datetime
    source: str
    payload: Any
