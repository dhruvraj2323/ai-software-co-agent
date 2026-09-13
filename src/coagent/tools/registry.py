"""Canonical tool definition and registry contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCapability(StrEnum):
    """Capability categories defined by the locked tool baseline."""

    WORKSPACE_READ = "workspace.read"
    WORKSPACE_WRITE = "workspace.write"
    WORKSPACE_DELETE = "workspace.delete"
    SEARCH_TEXT = "search.text"
    REPOSITORY_MAP = "repository.map"
    REPOSITORY_SYMBOLS = "repository.symbols"
    TERMINAL_PROCESS = "terminal.process"
    TERMINAL_POWERSHELL = "terminal.powershell"
    TESTING_RUN = "testing.run"
    TESTING_LINT = "testing.lint"
    TESTING_BUILD = "testing.build"
    GIT_STATUS = "git.status"
    GIT_DIFF = "git.diff"
    GIT_CHECKPOINT = "git.checkpoint"
    GIT_ROLLBACK = "git.rollback"
    GIT_COMMIT = "git.commit"
    MCP_INVOKE = "mcp.invoke"


class ToolRiskLevel(StrEnum):
    """Baseline risk classifications for registered capabilities."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VARIABLE = "VARIABLE"


class ToolSideEffect(StrEnum):
    """Side-effect classifications for tool definitions."""

    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"
    EXTERNAL = "EXTERNAL"


class ToolScope(StrEnum):
    """Resource-scope classifications for registered capabilities."""

    WORKSPACE = "WORKSPACE"
    FILE = "FILE"
    PROCESS = "PROCESS"
    NETWORK = "NETWORK"
    REPOSITORY = "REPOSITORY"
    EXTERNAL = "EXTERNAL"


class ToolOrigin(StrEnum):
    """Origin classifications for registered tools."""

    BUILTIN = "BUILTIN"
    MCP = "MCP"


class ToolDefinition(BaseModel):
    """Canonical metadata definition for one registered tool capability."""

    model_config = ConfigDict(extra="forbid")
    tool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    version: str = Field(min_length=1)
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    capability: ToolCapability
    risk_level: ToolRiskLevel
    side_effects: list[ToolSideEffect] = Field(min_length=1)
    resource_scope: ToolScope
    approval_profile: str = Field(min_length=1)
    executor: str = Field(min_length=1)
    origin: ToolOrigin
    enabled: bool = True


class ToolRegistry:
    """In-memory canonical registry for validated tool definitions."""

    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        """Register one tool definition and reject duplicate tool IDs."""
        if definition.tool_id in self._definitions:
            raise ValueError(f"tool already registered: {definition.tool_id}")
        self._definitions[definition.tool_id] = definition

    def get(self, tool_id: str) -> ToolDefinition | None:
        """Return a registered definition or None when unknown."""
        return self._definitions.get(tool_id)

    def require(self, tool_id: str) -> ToolDefinition:
        """Return a registered definition or raise for an unknown tool."""
        definition = self.get(tool_id)
        if definition is None:
            raise KeyError(f"unknown tool: {tool_id}")
        return definition

    def is_registered(self, tool_id: str) -> bool:
        """Return whether a tool ID is registered."""
        return tool_id in self._definitions

    def list(self) -> tuple[ToolDefinition, ...]:
        """Return all registered definitions in registration order."""
        return tuple(self._definitions.values())
