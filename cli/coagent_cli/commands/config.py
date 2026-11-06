"""CLI configuration display and validation commands (T095)."""

from __future__ import annotations

from typing import Any

from coagent.protocol.messages import PROTOCOL_VERSION


def get_default_config() -> dict[str, Any]:
    """Return default client configuration."""
    return {
        "protocol_version": PROTOCOL_VERSION,
        "runtime": {
            "autonomy_mode": "SUPERVISED_AUTO",
            "default_timeout_seconds": 60,
        },
        "client": {
            "name": "coagent-cli",
            "version": "0.1.0",
        },
    }


def validate_config(config: dict[str, Any]) -> bool:
    """Validate client configuration dictionary."""
    return config.get("protocol_version") == PROTOCOL_VERSION
