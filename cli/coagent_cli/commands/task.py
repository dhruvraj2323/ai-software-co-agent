"""CLI task management commands (T095)."""

from __future__ import annotations

from uuid import UUID

from coagent_cli.client import RuntimeClient
from coagent_cli.rendering import render_task_status


def create_task_cmd(client: RuntimeClient, goal: str, files: list[str] | None = None) -> str:
    """Submit a task creation request via protocol."""
    event = client.create_task(goal=goal, files=files)
    return render_task_status(event)


def status_task_cmd(client: RuntimeClient, task_id_str: str) -> str:
    """Read task status via protocol."""
    task_id = UUID(task_id_str)
    event = client.get_status(task_id=task_id)
    return render_task_status(event)


def cancel_task_cmd(client: RuntimeClient, task_id_str: str, reason: str | None = None) -> str:
    """Cancel task via protocol."""
    task_id = UUID(task_id_str)
    event = client.cancel_task(task_id=task_id, reason=reason)
    return render_task_status(event)
