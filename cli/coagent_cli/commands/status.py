"""CLI status inspection command (T095, T100)."""

from __future__ import annotations

from uuid import UUID

from coagent_cli.client import RuntimeClient
from coagent_cli.rendering import render_task_status


def status_cmd(client: RuntimeClient, task_id_str: str | None = None) -> str:
    """Query runtime task status."""
    task_id = UUID(task_id_str) if task_id_str else None
    event = client.get_status(task_id=task_id)
    return render_task_status(event)
