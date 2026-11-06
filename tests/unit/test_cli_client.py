"""Unit tests for the CLI RuntimeClient (T095)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from coagent_cli.client import RuntimeClient, RuntimeClientError

from coagent.protocol.messages import EventType
from coagent.runtime.service import RuntimeService


def test_client_session_and_task_lifecycle() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    # 1. Start Session
    session_evt = client.ensure_session()
    assert session_evt.type is EventType.CONTEXT_UPDATED
    assert session_evt.session_id == client.session_id
    assert session_evt.payload["state"] == "ACTIVE"

    # 2. Create Task
    task_evt = client.create_task(goal="Add unit tests", files=["test.py"])
    assert task_evt.type is EventType.TASK_CREATED
    assert task_evt.payload["state"] == "CREATED"
    assert task_evt.payload["goal"] == "Add unit tests"
    assert client.current_task_id is not None

    # 3. Status
    status_evt = client.get_status()
    assert status_evt.type is EventType.TASK_STATE_CHANGED
    assert status_evt.payload["state"] == "CREATED"

    # 4. Plan
    plan_evt = client.request_plan()
    assert plan_evt.type is EventType.PLAN_UPDATED
    assert plan_evt.payload["state"] == "READY"
    assert len(plan_evt.payload["plan"]) > 0

    # 5. Diff
    diff_evt = client.get_diff()
    assert diff_evt.type is EventType.CONTEXT_UPDATED

    # 6. Cancel
    cancel_evt = client.cancel_task(reason="Done testing")
    assert cancel_evt.type is EventType.TASK_CANCELLED
    assert cancel_evt.payload["state"] == "CANCELLED"


def test_client_approval_response() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)
    client.create_task(goal="Task needing approval")

    approval_evt = client.respond_approval(
        approval_id="app-123",
        approved=True,
        reason="User approved in CLI",
    )
    assert approval_evt.type is EventType.TASK_STATE_CHANGED
    assert approval_evt.payload["approved"] is True
    assert approval_evt.payload["approval_id"] == "app-123"


def test_client_raises_on_invalid_operation() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    # Calling get_status without creating a task raises ValueError
    with pytest.raises(ValueError, match="No active task_id"):
        client.get_status()

    # Calling status on non-existent task raises RuntimeClientError
    with pytest.raises(RuntimeClientError) as exc_info:
        client.get_status(task_id=uuid4())
    assert exc_info.value.code == "INVALID_CORRELATION_ID"
