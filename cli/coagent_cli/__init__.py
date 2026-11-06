"""CLI client interface package for the AI Software Co-Agent (T095)."""

from __future__ import annotations

from coagent_cli.client import RuntimeClient, RuntimeClientError
from coagent_cli.main import run_cli

__all__ = [
    "RuntimeClient",
    "RuntimeClientError",
    "run_cli",
]
