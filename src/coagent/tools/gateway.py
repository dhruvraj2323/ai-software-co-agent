"""Canonical gateway for routing registered tool requests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from coagent.tools.contracts import ToolRequest, ToolResult
from coagent.tools.registry import ToolDefinition, ToolRegistry


class ToolExecutor(Protocol):
    """Execution boundary used by the tool gateway."""

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> ToolResult:
        """Execute one gateway-authorized tool request."""
        ...


class ToolGateway:
    """Mandatory routing boundary for registered tool requests."""

    def __init__(
        self,
        registry: ToolRegistry,
        executor_resolver: Callable[[ToolDefinition], ToolExecutor],
    ) -> None:
        self._registry = registry
        self._executor_resolver = executor_resolver

    def route(self, request: ToolRequest) -> ToolResult:
        """Route a registered tool request to its resolved executor."""
        definition = self._registry.require(request.tool_id)
        if not definition.enabled:
            raise ValueError(f"tool is disabled: {request.tool_id}")
        if request.tool_version != definition.version:
            raise ValueError(
                f"tool version mismatch: {request.tool_id} "
                f"requested={request.tool_version} registered={definition.version}"
            )
        executor = self._executor_resolver(definition)
        return executor.execute(request, definition)
