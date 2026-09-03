"""Stable identifier primitives for the AI Software Co-Agent."""

from __future__ import annotations

from uuid import UUID, uuid4


def generate_session_id() -> UUID:
    """Generate a stable unique identifier for a session."""
    return uuid4()


def generate_task_id() -> UUID:
    """Generate a stable unique identifier for a task."""
    return uuid4()


def generate_request_id() -> UUID:
    """Generate a stable unique identifier for a request."""
    return uuid4()


def generate_event_id() -> UUID:
    """Generate a stable unique identifier for an event."""
    return uuid4()
