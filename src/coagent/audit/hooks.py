"""Audit hooks for material tool and policy decisions (T039)."""

from __future__ import annotations

from coagent.policy.contracts import PolicyDecision
from coagent.tools.contracts import ToolRequest
from coagent.tools.registry import ToolDefinition


class InMemoryAuditHook:
    """In-memory audit hook for capturing tool and policy decisions."""

    def __init__(self) -> None:
        self.records: list[tuple[PolicyDecision, ToolRequest, ToolDefinition]] = []

    def record_decision(
        self,
        decision: PolicyDecision,
        request: ToolRequest,
        definition: ToolDefinition,
    ) -> None:
        """Store the evaluated decision record."""
        self.records.append((decision, request, definition))
