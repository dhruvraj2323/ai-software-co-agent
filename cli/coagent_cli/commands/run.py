"""CLI task execution loop command (T095)."""

from __future__ import annotations

from coagent_cli.client import RuntimeClient
from coagent_cli.rendering import render_diff, render_plan, render_task_status


def run_task_cmd(
    client: RuntimeClient,
    goal: str,
    files: list[str] | None = None,
) -> str:
    """Execute the controlled task lifecycle through protocol requests."""
    # 1. Create Task
    create_evt = client.create_task(goal=goal, files=files)
    outputs = [render_task_status(create_evt)]

    # 2. Request Plan
    plan_evt = client.request_plan()
    outputs.append(render_plan(plan_evt))

    # 3. Read Diff
    diff_evt = client.get_diff()
    outputs.append(render_diff(diff_evt))

    # 4. Final Status
    final_evt = client.get_status()
    outputs.append(render_task_status(final_evt))

    return "\n\n".join(outputs)
