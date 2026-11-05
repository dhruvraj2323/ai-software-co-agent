"""Git integration adapter and status models (T045)."""

from __future__ import annotations

from coagent.git.adapter import GitAdapter, GitExecutionError
from coagent.git.status import GitStatus

__all__ = [
    "GitAdapter",
    "GitExecutionError",
    "GitStatus",
]
