"""Shared type definitions for the AI Software Co-Agent."""

from __future__ import annotations

from enum import StrEnum


class EventSeverity(StrEnum):
    """Severity levels for runtime events."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Recoverability(StrEnum):
    """Recoverability classification for normalized errors."""

    AUTO = "AUTO"
    ASSISTED = "ASSISTED"
    MANUAL = "MANUAL"
    NONE = "NONE"
