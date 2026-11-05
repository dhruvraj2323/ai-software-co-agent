"""Canonical gateway for routing registered tool requests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from coagent.policy.contracts import (
    PolicyDecision,
    PolicyDecisionOutcome,
    PolicyRequest,
)
from coagent.policy.evaluator import PolicyEvaluator
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


class ToolDecisionAuditHook(Protocol):
    """Callback contract for auditing tool decisions."""

    def record_decision(
        self,
        decision: PolicyDecision,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> None:
        """Record one evaluated policy decision."""
        ...


class ToolGateway:
    """Mandatory routing boundary for registered tool requests."""

    def __init__(
        self,
        registry: ToolRegistry,
        executor_resolver: Callable[[ToolDefinition], ToolExecutor],
        policy_evaluator: PolicyEvaluator | None = None,
        audit_hook: (
            ToolDecisionAuditHook
            | Callable[[PolicyDecision, ToolRequest, ToolDefinition], None]
            | None
        ) = None,
    ) -> None:
        self._registry = registry
        self._executor_resolver = executor_resolver
        self._policy_evaluator = policy_evaluator or PolicyEvaluator()
        self._audit_hook = audit_hook

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
        policy_request = PolicyRequest(
            request_id=request.request_id,
            task_id=request.task_id,
            correlation_id=request.correlation_id,
            tool_id=request.tool_id,
            tool_version=request.tool_version,
            arguments=request.arguments,
            requested_scope=request.requested_scope,
            autonomy_mode=request.autonomy_mode,
            source=request.source,
            risk_level=definition.risk_level,
            created_at=request.created_at,
        )
        decision = self._policy_evaluator.evaluate(policy_request, definition)
        if self._audit_hook is not None:
            if hasattr(self._audit_hook, "record_decision"):
                self._audit_hook.record_decision(decision, request, definition)
            elif callable(self._audit_hook):
                self._audit_hook(decision, request, definition)

        if decision.outcome is PolicyDecisionOutcome.DENY:
            raise ValueError(f"tool request denied by policy: {decision.reason}")
        if decision.outcome is PolicyDecisionOutcome.ASK:
            raise ValueError(f"tool request requires approval: {decision.reason}")
        executor = self._executor_resolver(definition)
        return executor.execute(request, definition)
