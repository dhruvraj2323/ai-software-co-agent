"""End-to-end integration test for client and runtime workflow (T095, T102)."""

from __future__ import annotations

from coagent_cli.client import RuntimeClient

from coagent.protocol.messages import EventType
from coagent.runtime.service import RuntimeService


def test_client_runtime_e2e_complete_workflow() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    # 1. Establish session
    session_evt = client.ensure_session()
    assert session_evt.type is EventType.CONTEXT_UPDATED
    assert session_evt.payload["state"] == "ACTIVE"

    # 2. Submit task
    task_evt = client.create_task(
        goal="Refactor client-runtime communication",
        files=["src/runtime.py"],
    )
    assert task_evt.type is EventType.TASK_CREATED
    assert task_evt.payload["state"] == "CREATED"
    task_id = client.current_task_id
    assert task_id is not None

    # 3. Generate plan
    plan_evt = client.request_plan()
    assert plan_evt.type is EventType.PLAN_UPDATED
    assert plan_evt.payload["state"] == "READY"
    assert len(plan_evt.payload["plan"]) >= 3

    # 4. Check status
    status_evt = client.get_status()
    assert status_evt.type is EventType.TASK_STATE_CHANGED
    assert status_evt.payload["state"] == "READY"

    # 5. Process approval
    approval_evt = client.respond_approval(
        approval_id="approval-e2e-1",
        approved=True,
        reason="Approved by developer",
    )
    assert approval_evt.type is EventType.TASK_STATE_CHANGED
    assert approval_evt.payload["approved"] is True

    # 6. Read diff
    diff_evt = client.get_diff()
    assert diff_evt.type is EventType.CONTEXT_UPDATED
    assert "diff" in diff_evt.payload

    # 7. Check completion status
    comp_evt = client.get_completion_status()
    assert comp_evt.type in (EventType.TASK_COMPLETED, EventType.TASK_STATE_CHANGED)

    # 8. Cancel task cleanly
    cancel_evt = client.cancel_task(reason="Lifecycle verification complete")
    assert cancel_evt.type is EventType.TASK_CANCELLED
    assert cancel_evt.payload["state"] == "CANCELLED"
