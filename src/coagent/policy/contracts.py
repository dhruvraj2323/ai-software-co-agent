"""Canonical policy request and decision contracts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.tools.contracts import AutonomyMode, Scope, ToolRequestSource
from coagent.tools.registry import ToolRiskLevel


class PolicyDecisionOutcome(StrEnum):
    """Canonical policy outcomes defined by the tool permission baseline."""

    ALLOW = "ALLOW"
    ASK = "ASK"
    DENY = "DENY"
    RESTRICT = "RESTRICT"


class PolicyRequest(BaseModel):
    """Canonical authorization input for one tool request."""

    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    task_id: UUID
    correlation_id: UUID
    tool_id: str = Field(min_length=1)
    tool_version: str = Field(min_length=1)
    arguments: dict[str, Any]
    requested_scope: Scope
    autonomy_mode: AutonomyMode
    source: ToolRequestSource
    risk_level: ToolRiskLevel
    created_at: datetime


class PolicyDecision(BaseModel):
    """Canonical policy outcome and decision evidence."""

    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    task_id: UUID
    correlation_id: UUID
    outcome: PolicyDecisionOutcome
    reason: str = Field(min_length=1)
    rule_id: str = Field(min_length=1)
    evaluated_scope: Scope
    risk_level: ToolRiskLevel
    created_at: datetime
