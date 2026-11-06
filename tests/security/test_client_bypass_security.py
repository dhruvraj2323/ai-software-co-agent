"""Security and bypass tests for CLI and VS Code clients (T103, VCI-001 §2, §23)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.policy.contracts import PolicyDecisionOutcome, PolicyRequest
from coagent.policy.evaluator import PolicyEvaluator
from coagent.protocol.errors import ProtocolErrorCode, ProtocolErrorEnvelope
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    ClientRequest,
    RequestType,
)
from coagent.runtime.service import RuntimeService
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequestSource,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)


def make_client_request(
    req_type: RequestType,
    *,
    session_id=None,
    task_id=None,
    payload=None,
    client_context=None,
) -> ClientRequest:
    return ClientRequest(
        protocol_version=PROTOCOL_VERSION,
        request_id=uuid4(),
        session_id=session_id or uuid4(),
        task_id=task_id,
        type=req_type,
        payload=payload or {},
        client_context=client_context or {},
        created_at=datetime.now(UTC),
    )


def test_client_cannot_access_task_across_sessions() -> None:
    """A client in Session B cannot query or manipulate a task created in Session A."""
    service = RuntimeService()

    session_a = uuid4()
    session_b = uuid4()

    # Session A creates a task
    service.handle(make_client_request(RequestType.SESSION_START, session_id=session_a))
    create_evt = service.handle(make_client_request(RequestType.TASK_CREATE, session_id=session_a))
    task_id = create_evt.task_id
    assert task_id is not None

    # Session B starts
    service.handle(make_client_request(RequestType.SESSION_START, session_id=session_b))

    # Session B attempts to read status of Session A's task
    hijack_req = make_client_request(
        RequestType.TASK_STATUS,
        session_id=session_b,
        task_id=task_id,
    )
    response = service.handle(hijack_req)

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.INVALID_CORRELATION_ID
    assert "does not belong to session" in response.error.details.get("reason", "")


def test_client_cannot_cancel_task_across_sessions() -> None:
    """A client in Session B cannot cancel a task created in Session A."""
    service = RuntimeService()

    session_a = uuid4()
    session_b = uuid4()

    service.handle(make_client_request(RequestType.SESSION_START, session_id=session_a))
    create_evt = service.handle(make_client_request(RequestType.TASK_CREATE, session_id=session_a))
    task_id = create_evt.task_id

    service.handle(make_client_request(RequestType.SESSION_START, session_id=session_b))

    cancel_req = make_client_request(
        RequestType.TASK_CANCEL,
        session_id=session_b,
        task_id=task_id,
    )
    response = service.handle(cancel_req)

    assert isinstance(response, ProtocolErrorEnvelope)
    assert response.error.code is ProtocolErrorCode.INVALID_CORRELATION_ID


def test_client_context_cannot_bypass_policy_engine() -> None:
    """Client claims of admin privileges or bypass flags must be ignored by policy."""
    evaluator = PolicyEvaluator()
    task_id = uuid4()
    scope = Scope(workspace_id=uuid4(), root="/workspace")

    pol_req = PolicyRequest(
        request_id=uuid4(),
        task_id=task_id,
        correlation_id=uuid4(),
        tool_id="workspace.write",
        tool_version="1.0",
        arguments={
            "path": "../../../etc/passwd",
            "content": "root::0:0:::",
            "override_policy": True,
            "bypass_auth": True,
        },
        requested_scope=scope,
        autonomy_mode=AutonomyMode.AUTONOMOUS,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.HIGH,
        created_at=datetime.now(UTC),
    )
    definition = ToolDefinition(
        tool_id="workspace.write",
        name="Workspace Write",
        description="Write files",
        version="1.0",
        input_schema={},
        output_schema={},
        capability=ToolCapability.WORKSPACE_WRITE,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.WRITE],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="workspace.write",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )

    decision = evaluator.evaluate(pol_req, definition)
    # The policy engine must never grant automatic allow to dangerous paths
    assert decision.outcome is not PolicyDecisionOutcome.ALLOW or decision.requires_approval is True


def test_client_cannot_send_forged_request_envelope() -> None:
    """Client envelopes with injected extra fields are rejected at the protocol boundary."""
    with pytest.raises(ValidationError):
        ClientRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=uuid4(),
            session_id=uuid4(),
            task_id=uuid4(),
            type=RequestType.TASK_CREATE,
            payload={},
            client_context={},
            created_at=datetime.now(UTC),
            injected_admin_privilege=True,  # type: ignore[call-arg]
        )
