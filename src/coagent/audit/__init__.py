"""Audit, evidence recording, and observability subsystem (EPIC-10, T087-T094)."""

from __future__ import annotations

from coagent.audit.hooks import InMemoryAuditHook
from coagent.audit.recorder import AuditRecorder
from coagent.audit.redaction import OutputRedactor, SecretLeakageError
from coagent.audit.trace import TaskTrace, TaskTraceReconstructor

__all__ = [
    "AuditRecorder",
    "InMemoryAuditHook",
    "OutputRedactor",
    "SecretLeakageError",
    "TaskTrace",
    "TaskTraceReconstructor",
]
