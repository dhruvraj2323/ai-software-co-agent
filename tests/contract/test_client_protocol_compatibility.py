"""Client protocol compatibility test suite (T102, VCI-001 §8, §9)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.protocol.errors import ProtocolErrorCode, ProtocolErrorEnvelope
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    EventType,
    RequestType,
    RuntimeEvent,
)
from coagent.runtime.service import RuntimeService


def make_request(
    req_type: RequestType,
    *,
    session_id=None,
    task_id=None,
    payload=None,
    client_context=None,
    protocol_version=PROTOCOL_VERSION,
) -> ClientRequest:
    return ClientRequest(
        protocol_version=protocol_version,
        request_id=uuid4(),
        session_id=session_id or uuid4(),
        task_id=task_id,
        type=req_type,
        payload=payload or {},
        client_context=client_context or {"client": "test-client"},
        created_at=datetime.now(UTC),
    )


def test_protocol_version_enforcement() -> None:
    # Supported version
    req = make_request(RequestType.SESSION_START, protocol_version=PROTOCOL_VERSION)
    assert req.protocol_version == "1.0"

    # Unsupported version raises ValidationError
    with pytest.raises(ValidationError):
        make_request(RequestType.SESSION_START, protocol_version="2.0")


def test_cli_and_vscode_protocol_interoperability() -> None:
    """Verify both CLI and VS Code client requests interoperate with the runtime service."""
    service = RuntimeService()
    session_id = uuid4()

    # 1. Start session from VS Code client
    vscode_start = make_request(
        RequestType.SESSION_START,
        session_id=session_id,
        client_context={"client": "vscode-extension", "version": "0.1.0"},
    )
    res1 = service.handle(vscode_start)
    assert isinstance(res1, RuntimeEvent)
    assert res1.type is EventType.CONTEXT_UPDATED

    # 2. Create task from CLI client in same session
    cli_create = make_request(
        RequestType.TASK_CREATE,
        session_id=session_id,
        payload={"goal": "Cross-client task", "files": ["main.py"]},
        client_context={"client": "coagent-cli", "version": "0.1.0"},
    )
    res2 = service.handle(cli_create)
    assert isinstance(res2, RuntimeEvent)
    assert res2.type is EventType.TASK_CREATED
    task_id = res2.task_id
    assert task_id is not None

    # 3. Request plan from VS Code client
    vscode_plan = make_request(
        RequestType.PLAN_REQUEST,
        session_id=session_id,
        task_id=task_id,
        client_context={"client": "vscode-extension"},
    )
    res3 = service.handle(vscode_plan)
    assert isinstance(res3, RuntimeEvent)
    assert res3.type is EventType.PLAN_UPDATED
    assert res3.payload["state"] == "READY"

    # 4. Check status from CLI client
    cli_status = make_request(
        RequestType.TASK_STATUS,
        session_id=session_id,
        task_id=task_id,
        client_context={"client": "coagent-cli"},
    )
    res4 = service.handle(cli_status)
    assert isinstance(res4, RuntimeEvent)
    assert res4.type is EventType.TASK_STATE_CHANGED
    assert res4.payload["state"] == "READY"

    # 5. Respond to approval from VS Code client
    vscode_approval = make_request(
        RequestType.APPROVAL_RESPOND,
        session_id=session_id,
        task_id=task_id,
        payload={"approval_id": "app-001", "approved": True, "reason": "Authorized by user"},
        client_context={"client": "vscode-extension"},
    )
    res5 = service.handle(vscode_approval)
    assert isinstance(res5, RuntimeEvent)
    assert res5.payload["approved"] is True

    # 6. Read diff from CLI client
    cli_diff = make_request(
        RequestType.DIFF_OPEN,
        session_id=session_id,
        task_id=task_id,
    )
    res6 = service.handle(cli_diff)
    assert isinstance(res6, RuntimeEvent)

    # 7. Cancel from VS Code client
    vscode_cancel = make_request(
        RequestType.TASK_CANCEL,
        session_id=session_id,
        task_id=task_id,
        payload={"reason": "Cancelled from editor"},
    )
    res7 = service.handle(vscode_cancel)
    assert isinstance(res7, RuntimeEvent)
    assert res7.type is EventType.TASK_CANCELLED
    assert res7.payload["state"] == "CANCELLED"


def test_protocol_error_rejection_for_missing_task_id() -> None:
    service = RuntimeService()
    session_id = uuid4()
    service.handle(make_request(RequestType.SESSION_START, session_id=session_id))

    # PLAN_REQUEST without task_id
    bad_req = make_request(RequestType.PLAN_REQUEST, session_id=session_id, task_id=None)
    response = service.handle(bad_req)

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.MISSING_REQUIRED_FIELD
