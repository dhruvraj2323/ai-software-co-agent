"""Tests for stable identifier generation."""

from uuid import UUID

from coagent.core.ids import (
    generate_event_id,
    generate_request_id,
    generate_session_id,
    generate_task_id,
)


def test_generate_session_id_returns_uuid() -> None:
    session_id = generate_session_id()

    assert isinstance(session_id, UUID)


def test_generate_task_id_returns_uuid() -> None:
    task_id = generate_task_id()

    assert isinstance(task_id, UUID)


def test_generate_request_id_returns_uuid() -> None:
    request_id = generate_request_id()

    assert isinstance(request_id, UUID)


def test_generate_event_id_returns_uuid() -> None:
    event_id = generate_event_id()

    assert isinstance(event_id, UUID)


def test_generated_ids_are_unique() -> None:
    ids = {
        generate_session_id(),
        generate_task_id(),
        generate_request_id(),
        generate_event_id(),
    }

    assert len(ids) == 4
