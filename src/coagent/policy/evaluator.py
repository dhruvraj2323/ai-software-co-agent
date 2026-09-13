"""Deterministic policy scope and risk evaluation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from coagent.policy.contracts import (
    PolicyDecision,
    PolicyDecisionOutcome,
    PolicyRequest,
)
from coagent.security import (
    ProtectedPathPolicy,
    WorkspaceEscapeError,
)
from coagent.tools.registry import (
    ToolDefinition,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.workspace import WorkspaceScope


class PolicyEvaluator:
    """Evaluate tool scope, risk, and autonomy deterministically."""

    def __init__(
        self,
        protected_path_policy: ProtectedPathPolicy | None = None,
    ) -> None:
        self._protected_path_policy = protected_path_policy or ProtectedPathPolicy()

    def evaluate(
        self,
        request: PolicyRequest,
        definition: ToolDefinition,
        *,
        now: datetime | None = None,
    ) -> PolicyDecision:
        """Evaluate one normalized policy request against tool metadata."""
        decision_time = now or request.created_at
        identity_decision = self._evaluate_identity(
            request,
            definition,
            decision_time,
        )
        if identity_decision is not None:
            return identity_decision
        scope_decision = self._evaluate_scope(request, definition, decision_time)
        if scope_decision is not None:
            return scope_decision
        return self._evaluate_risk(
            request,
            definition,
            decision_time,
        )

    @staticmethod
    def _evaluate_identity(
        request: PolicyRequest,
        definition: ToolDefinition,
        created_at: datetime,
    ) -> PolicyDecision | None:
        """Reject unknown, disabled, or version-mismatched tool requests."""
        if request.tool_id != definition.tool_id:
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.DENY,
                "Requested tool does not match the registered tool.",
                "policy.tool.identity.mismatch",
                created_at,
            )
        if request.tool_version != definition.version:
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.DENY,
                "Requested tool version does not match the registered version.",
                "policy.tool.version.mismatch",
                created_at,
            )
        if not definition.enabled:
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.DENY,
                "The requested tool is disabled.",
                "policy.tool.disabled",
                created_at,
            )
        return None

    def _evaluate_scope(
        self,
        request: PolicyRequest,
        definition: ToolDefinition,
        created_at: datetime,
    ) -> PolicyDecision | None:
        """Evaluate target containment and protected-resource status."""
        if definition.resource_scope in {
            ToolScope.WORKSPACE,
            ToolScope.FILE,
        }:
            target = self._target_path(request)
            if target is None:
                return self._decision(
                    request,
                    PolicyDecisionOutcome.ASK,
                    "The scoped tool request has no unambiguous target.",
                    "policy.scope.ambiguous",
                    created_at,
                )
            workspace_scope = WorkspaceScope(
                task_id=request.task_id,
                workspace_id=request.requested_scope.workspace_id,
                root=request.requested_scope.root,
            )
            try:
                category = self._protected_path_policy.classify(
                    workspace_scope,
                    target,
                )
            except WorkspaceEscapeError:
                return self._decision(
                    request,
                    PolicyDecisionOutcome.DENY,
                    "The requested target is outside the authorized workspace.",
                    "policy.scope.out_of_scope",
                    created_at,
                )
            if category is not None:
                return self._decision(
                    request,
                    PolicyDecisionOutcome.DENY,
                    (
                        "The requested target is protected and cannot be "
                        "authorized by this evaluator."
                    ),
                    "policy.resource.protected",
                    created_at,
                )
        if definition.resource_scope is ToolScope.REPOSITORY:
            target = self._target_path(request)
            if target is not None:
                workspace_scope = WorkspaceScope(
                    task_id=request.task_id,
                    workspace_id=request.requested_scope.workspace_id,
                    root=request.requested_scope.root,
                )
                try:
                    Path(target).resolve().relative_to(Path(workspace_scope.root).resolve())
                except ValueError:
                    return self._decision(
                        request,
                        PolicyDecisionOutcome.DENY,
                        "The repository target is outside the authorized workspace.",
                        "policy.scope.out_of_scope",
                        created_at,
                    )
        if definition.resource_scope is ToolScope.EXTERNAL:
            return self._decision(
                request,
                PolicyDecisionOutcome.ASK,
                "External resources require explicit authorization.",
                "policy.resource.external",
                created_at,
            )
        return None

    @staticmethod
    def _evaluate_risk(
        request: PolicyRequest,
        definition: ToolDefinition,
        created_at: datetime,
    ) -> PolicyDecision:
        """Evaluate registered risk and side-effect metadata."""
        side_effects = set(definition.side_effects)
        if (
            definition.risk_level is ToolRiskLevel.HIGH
            or ToolSideEffect.DESTRUCTIVE in side_effects
        ):
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.ASK,
                "High-risk or destructive operations require approval.",
                "policy.risk.high",
                created_at,
            )
        if ToolSideEffect.EXTERNAL in side_effects:
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.ASK,
                "External side effects require explicit authorization.",
                "policy.risk.external",
                created_at,
            )
        if (
            request.autonomy_mode.value == "RESTRICTED"
            and definition.risk_level is not ToolRiskLevel.LOW
        ):
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.DENY,
                "Restricted autonomy mode does not authorize this risk level.",
                "policy.autonomy.restricted",
                created_at,
            )
        if (
            definition.risk_level is ToolRiskLevel.MEDIUM
            or ToolSideEffect.WRITE in side_effects
            or ToolSideEffect.EXECUTE in side_effects
        ):
            return PolicyEvaluator._decision(
                request,
                PolicyDecisionOutcome.RESTRICT,
                "Operation is allowed only under its registered scope and controls.",
                "policy.risk.medium",
                created_at,
            )
        return PolicyEvaluator._decision(
            request,
            PolicyDecisionOutcome.ALLOW,
            "Tool is low-risk and remains within the evaluated scope.",
            "policy.allow.scoped",
            created_at,
        )

    @staticmethod
    def _target_path(request: PolicyRequest) -> str | None:
        """Extract a single unambiguous filesystem/resource target."""
        for key in ("path", "target", "cwd", "repo", "root"):
            value = request.arguments.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return None

    @staticmethod
    def _decision(
        request: PolicyRequest,
        outcome: PolicyDecisionOutcome,
        reason: str,
        rule_id: str,
        created_at: datetime,
    ) -> PolicyDecision:
        """Build the canonical policy decision contract."""
        return PolicyDecision(
            request_id=request.request_id,
            task_id=request.task_id,
            correlation_id=request.correlation_id,
            outcome=outcome,
            reason=reason,
            rule_id=rule_id,
            evaluated_scope=request.requested_scope,
            risk_level=request.risk_level,
            created_at=created_at,
        )
