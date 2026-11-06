"""Model Context Protocol (MCP) adapter and security boundary.

According to locked specifications (ADM-012, TPS-A08, ST-MCP-001):
- MCP servers are external, untrusted capabilities.
- Each MCP capability is represented internally by a ToolDefinition with ToolOrigin.MCP.
- All MCP invocations create normal ToolRequests and route through ToolGateway and PolicyEngine.
- MCP server responses are treated as untrusted tool output.
- MCP cannot obtain filesystem, process, or Git authority outside the internal execution boundary.
- MCP capability metadata cannot override internal security policy.
- MCP invocations are auditable with server/tool identity and correlation ID.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.tools.contracts import (
    ScopeEffect,
    ToolRequest,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)


class McpSecurityViolation(RuntimeError):
    """Raised when an MCP tool attempts to bypass policy or claim unauthorized authority."""


@dataclass(frozen=True)
class McpServerConfig:
    """Configuration for a connected MCP server."""

    server_id: str
    name: str
    transport: str = "stdio"  # "stdio" or "sse"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class McpToolDefinition:
    """Metadata for a discovered MCP tool."""

    server_id: str
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    capability: ToolCapability = ToolCapability.MCP_INVOKE
    risk_level: ToolRiskLevel = ToolRiskLevel.HIGH
    side_effect: ToolSideEffect = ToolSideEffect.EXTERNAL
    scope: ToolScope = ToolScope.NETWORK

    def to_tool_definition(self) -> ToolDefinition:
        """Convert MCP tool metadata to an internal ToolDefinition.

        Enforces ToolOrigin.MCP and internal security bounds.
        """
        tool_id = f"mcp.{self.server_id}.{self.name}"
        return ToolDefinition(
            tool_id=tool_id,
            name=self.name,
            description=f"[MCP:{self.server_id}] {self.description}",
            version="1.0",
            input_schema=self.input_schema,
            output_schema={"type": "object"},
            capability=self.capability,
            risk_level=self.risk_level,
            side_effects=[self.side_effect],
            resource_scope=self.scope,
            approval_profile="mcp-policy",
            executor=f"mcp.{self.server_id}",
            origin=ToolOrigin.MCP,
            enabled=True,
        )


class McpAdapter:
    """Adapter bridging MCP servers with the central ToolGateway.

    All invocations must pass through ToolGateway. The adapter acts as
    the execution backend once PolicyEngine has granted ALLOW.
    """

    def __init__(self) -> None:
        self._servers: dict[str, McpServerConfig] = {}
        self._tools: dict[str, McpToolDefinition] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register_server(self, config: McpServerConfig) -> None:
        """Register an MCP server."""
        self._servers[config.server_id] = config

    def register_tool(
        self,
        tool: McpToolDefinition,
        handler: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> ToolDefinition:
        """Register a discovered MCP tool and return its internal ToolDefinition."""
        if tool.server_id not in self._servers:
            raise ValueError(f"Unknown MCP server '{tool.server_id}'")

        tool_id = f"mcp.{tool.server_id}.{tool.name}"
        self._tools[tool_id] = tool
        if handler:
            self._handlers[tool_id] = handler
        return tool.to_tool_definition()

    def _error_result(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        now = datetime.now(UTC)
        error = ErrorRecord(
            error_id=uuid4(),
            task_id=request.task_id,
            correlation_id=request.correlation_id,
            category="MCP",
            code=code,
            source="coagent.tools.mcp",
            message=message,
            severity=EventSeverity.ERROR,
            recoverability=Recoverability.MANUAL,
            occurred_at=now,
            normalized_at=now,
        )
        return ToolResult(
            request_id=request.request_id,
            success=False,
            status=ToolResultStatus.FAILED,
            output={},
            error=error,
            scope_effect=ScopeEffect.NONE,
            created_at=now,
        )

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> ToolResult:
        """Execute an MCP tool call on behalf of the ToolGateway.

        MUST only be called by ToolGateway after policy authorization.
        Treats output as untrusted external data.
        """
        tool_id = request.tool_id
        tool_def = self._tools.get(tool_id)
        if not tool_def:
            return self._error_result(
                request,
                code="MCP_TOOL_NOT_FOUND",
                message=f"MCP tool '{tool_id}' not found in adapter registry.",
            )

        handler = self._handlers.get(tool_id)
        if not handler:
            return self._error_result(
                request,
                code="MCP_HANDLER_NOT_FOUND",
                message=f"No execution handler configured for MCP tool '{tool_id}'.",
            )

        try:
            raw_output = handler(request.arguments)
            # Ensure raw_output is wrapped safely and treated as untrusted data
            sanitized_output = {
                "untrusted_mcp_data": raw_output,
                "server_id": tool_def.server_id,
                "tool_name": tool_def.name,
            }
            return ToolResult(
                request_id=request.request_id,
                success=True,
                status=ToolResultStatus.SUCCESS,
                output=sanitized_output,
                scope_effect=ScopeEffect.NONE,
                created_at=datetime.now(UTC),
            )
        except Exception as exc:
            return self._error_result(
                request,
                code="MCP_EXECUTION_ERROR",
                message=f"MCP server execution error: {exc}",
            )
