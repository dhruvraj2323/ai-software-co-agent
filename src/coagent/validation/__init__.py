"""Validation runner, evidence models, and authoritative Completion Gate."""

from coagent.validation.completion import CompletionEvaluation, CompletionGate
from coagent.validation.evidence import (
    GateCategory,
    GateStatus,
    ValidationResult,
)
from coagent.validation.runner import (
    ValidationGateDefinition,
    ValidationRunner,
)

__all__ = [
    "CompletionEvaluation",
    "CompletionGate",
    "GateCategory",
    "GateStatus",
    "ValidationGateDefinition",
    "ValidationResult",
    "ValidationRunner",
]
