"""Tests for runtime-owned session lifecycle."""

from time import sleep
from uuid import UUID

import pytest

from coagent.runtime.session import (
    InvalidSessionTransitionError,
    Session,
    SessionState,
)


def test_session_starts_active_with_uuid() -> None:
    session = Session()

    assert isinstance(session.session_id, UUID)
    assert session.state is SessionState.ACTIVE
    assert session.created_at == session.updated_at


def test_active_to_disconnected() -> None:
    session = Session()

    session.disconnect()

    assert session.state is SessionState.DISCONNECTED


def test_disconnected_to_active_preserves_identity() -> None:
    session = Session()
    session_id = session.session_id

    session.disconnect()
    session.reconnect()

    assert session.state is SessionState.ACTIVE
    assert session.session_id == session_id


def test_active_to_terminated() -> None:
    session = Session()

    session.terminate()

    assert session.state is SessionState.TERMINATED


def test_disconnected_to_terminated() -> None:
    session = Session()

    session.disconnect()
    session.terminate()

    assert session.state is SessionState.TERMINATED


@pytest.mark.parametrize(
    "operation",
    ["disconnect", "reconnect", "terminate"],
)
def test_terminated_session_rejects_all_transitions(
    operation: str,
) -> None:
    session = Session()
    session.terminate()

    with pytest.raises(InvalidSessionTransitionError):
        getattr(session, operation)()


def test_invalid_active_reconnect_is_rejected() -> None:
    session = Session()

    with pytest.raises(InvalidSessionTransitionError):
        session.reconnect()


def test_updated_at_changes_on_transition() -> None:
    session = Session()
    original_updated_at = session.updated_at

    sleep(0.001)
    session.disconnect()

    assert session.updated_at > original_updated_at
