"""Unit and conformance tests for ModelGateway and ModelAdapters (T066, T067)."""

from __future__ import annotations

import pytest

from coagent.models.adapter import MockModelAdapter
from coagent.models.contracts import (
    MessageRole,
    ModelMessage,
    ModelResponse,
    ToolCallProposal,
)
from coagent.models.gateway import ModelGateway


def test_model_gateway_default_generation() -> None:
    gateway = ModelGateway()
    messages = [
        ModelMessage(role=MessageRole.USER, content="Hello, model."),
    ]

    response = gateway.generate(messages)
    assert response.content == "Mock model default response."
    assert response.finish_reason == "stop"
    assert gateway.call_count == 1
    assert gateway.total_usage.total_tokens > 0


def test_model_gateway_multiple_adapters() -> None:
    primary = MockModelAdapter(name="primary")
    fast = MockModelAdapter(name="fast")
    fast.queue_response(
        ModelResponse(
            content="Fast model output",
            model_name="fast",
        )
    )

    gateway = ModelGateway(default_adapter=primary)
    gateway.register_adapter("fast", fast)

    msg = [ModelMessage(role=MessageRole.USER, content="Test")]

    # Query default
    res_default = gateway.generate(msg)
    assert res_default.model_name == "primary"

    # Query fast adapter
    res_fast = gateway.generate(msg, model_name="fast")
    assert res_fast.model_name == "fast"
    assert res_fast.content == "Fast model output"


def test_model_gateway_unknown_adapter_raises() -> None:
    gateway = ModelGateway()
    msg = [ModelMessage(role=MessageRole.USER, content="Test")]

    with pytest.raises(KeyError, match="No model adapter registered"):
        gateway.generate(msg, model_name="nonexistent-model")


def test_model_adapter_tool_call_conformance() -> None:
    """Conformance test verifying adapters return well-formed ToolCallProposal objects."""
    adapter = MockModelAdapter(name="conformance-test")
    proposal = ToolCallProposal(
        name="workspace.read_file",
        arguments={"path": "src/main.py"},
    )
    adapter.queue_response(
        ModelResponse(
            content="I will read the file.",
            tool_calls=[proposal],
        )
    )

    response = adapter.generate([ModelMessage(role=MessageRole.USER, content="Read main.py")])

    assert len(response.tool_calls) == 1
    call = response.tool_calls[0]
    assert call.name == "workspace.read_file"
    assert call.arguments["path"] == "src/main.py"
    assert call.id.startswith("call_")
