"""Canonical approval lifecycle for policy ASK decisions."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.tools.registry import ToolRiskLevel


class ApprovalStatus(StrEnum):
    """Lifecycle states for one policy approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalDecision(StrEnum):
    """Human decision values recorded by the approval lifecycle."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ApprovalRequest(BaseModel):
    """Immutable approval request bound to one evaluated tool request."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    approval_id: UUID
    request_id: UUID
    task_id: UUID
    correlation_id: UUID
    tool_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target: str = Field(min_length=1)
    risk_level: ToolRiskLevel
    reason: str = Field(min_length=1)
    alternatives: list[str] = Field(default_factory=list)
    expires_at: datetime
    created_at: datetime


class ApprovalRecord(BaseModel):
    """Mutable lifecycle state for one approval request."""

    model_config = ConfigDict(extra="forbid")
    request: ApprovalRequest
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision: ApprovalDecision | None = None
    decided_at: datetime | None = None

    def is_expired(self, now: datetime) -> bool:
        """Return whether the approval has reached or passed its expiry."""
        return now >= self.request.expires_at

    def expire(self, now: datetime) -> None:
        """Move a pending approval to EXPIRED when its deadline is reached."""
        if self.status is not ApprovalStatus.PENDING:
            raise ValueError(f"approval is not pending: {self.request.approval_id}")
        if now < self.request.expires_at:
            raise ValueError(f"approval has not expired: {self.request.approval_id}")
        self.status = ApprovalStatus.EXPIRED
        self.decision = None
        self.decided_at = now

    def decide(
        self,
        decision: ApprovalDecision,
        now: datetime,
    ) -> None:
        """Record an approval decision for a still-valid pending request."""
        if self.status is not ApprovalStatus.PENDING:
            raise ValueError(f"approval is not pending: {self.request.approval_id}")
        if self.is_expired(now):
            self.status = ApprovalStatus.EXPIRED
            self.decision = None
            self.decided_at = now
            raise ValueError(f"approval has expired: {self.request.approval_id}")
        self.decision = decision
        self.decided_at = now
        self.status = (
            ApprovalStatus.APPROVED
            if decision is ApprovalDecision.APPROVE
            else ApprovalStatus.REJECTED
        )

    @property
    def may_continue(self) -> bool:
        """Return whether this approval authorizes continuation."""
        return self.status is ApprovalStatus.APPROVED


class ApprovalStore:
    """In-memory lifecycle store enforcing request-bound approvals."""

    def __init__(self) -> None:
        self._records: dict[UUID, ApprovalRecord] = {}

    def create(self, request: ApprovalRequest) -> ApprovalRecord:
        """Create one pending approval request."""
        if request.approval_id in self._records:
            raise ValueError(f"approval already exists: {request.approval_id}")
        record = ApprovalRecord(request=request)
        self._records[request.approval_id] = record
        return record

    def get(self, approval_id: UUID) -> ApprovalRecord:
        """Return an approval record by its stable approval ID."""
        try:
            return self._records[approval_id]
        except KeyError as exc:
            raise KeyError(f"unknown approval: {approval_id}") from exc

    def require_request(
        self,
        approval_id: UUID,
        request_id: UUID,
    ) -> ApprovalRecord:
        """Return an approval only when it belongs to the requested action."""
        record = self.get(approval_id)
        if record.request.request_id != request_id:
            raise ValueError("approval is not bound to the requested tool request")
        return record

    def decide(
        self,
        approval_id: UUID,
        request_id: UUID,
        decision: ApprovalDecision,
        now: datetime,
    ) -> ApprovalRecord:
        """Record a request-bound human approval decision."""
        record = self.require_request(approval_id, request_id)
        record.decide(decision, now)
        return record

    def expire(
        self,
        approval_id: UUID,
        request_id: UUID,
        now: datetime,
    ) -> ApprovalRecord:
        """Expire a request-bound pending approval."""
        record = self.require_request(approval_id, request_id)
        record.expire(now)
        return record
