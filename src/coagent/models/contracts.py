"""Model contracts, messages, proposals, and responses (T066)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    """Role classification for model prompt messages."""

    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"


class ModelMessage(BaseModel):
    """Normalized message unit passed to model adapters."""

    model_config = ConfigDict(extra="forbid")

    role: MessageRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None


class ToolCallProposal(BaseModel):
    """Untrusted model proposal requesting a tool invocation.

    NOTE: Model proposals are NOT authorization. They must be validated
    and routed through ToolGateway and PolicyEngine before execution.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:12]}")
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ModelUsage(BaseModel):
    """Token consumption statistics returned by a provider."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ModelResponse(BaseModel):
    """Normalized response returned by any ModelAdapter."""

    model_config = ConfigDict(extra="forbid")

    content: str = ""
    tool_calls: list[ToolCallProposal] = Field(default_factory=list)
    usage: ModelUsage = Field(default_factory=ModelUsage)
    model_name: str = "default"
    finish_reason: str = "stop"
