"""Model Gateway and provider adapter abstraction."""

from coagent.models.adapter import MockModelAdapter, ModelAdapter
from coagent.models.contracts import (
    MessageRole,
    ModelMessage,
    ModelResponse,
    ModelUsage,
    ToolCallProposal,
)
from coagent.models.gateway import ModelGateway

__all__ = [
    "MessageRole",
    "MockModelAdapter",
    "ModelAdapter",
    "ModelGateway",
    "ModelMessage",
    "ModelResponse",
    "ModelUsage",
    "ToolCallProposal",
]
