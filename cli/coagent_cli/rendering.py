"""Terminal formatting and presentation utilities for CLI output (T095, T099, T100)."""

from __future__ import annotations

from typing import Any

from coagent.protocol.messages import RuntimeEvent


def render_task_status(event: RuntimeEvent) -> str:
    """Format a task status event into human-readable text."""
    p = event.payload
    task_id = p.get("task_id", str(event.task_id or "unknown"))
    state = p.get("state", "UNKNOWN")
    lines = [
        "========================================",
        f" Task Status: {task_id}",
        "========================================",
        f" State:      {state}",
        f" Session:    {event.session_id}",
        f" Timestamp:  {event.created_at.isoformat()}",
    ]
    if "goal" in p:
        lines.append(f" Goal:       {p['goal']}")
    if "reason" in p:
        lines.append(f" Detail:     {p['reason']}")
    return "\n".join(lines)


def render_plan(event: RuntimeEvent) -> str:
    """Format a plan.updated event into an ordered step-by-step display."""
    p = event.payload
    task_id = p.get("task_id", str(event.task_id or "unknown"))
    state = p.get("state", "READY")
    plan_steps: list[dict[str, Any]] = p.get("plan", [])

    lines = [
        "========================================",
        f" Task Plan: {task_id} [{state}]",
        "========================================",
    ]
    if not plan_steps:
        lines.append("  (No plan steps generated)")
    else:
        for item in plan_steps:
            step_num = item.get("step", "#")
            desc = item.get("description", "")
            lines.append(f"  [{step_num}] {desc}")
    return "\n".join(lines)


def render_diff(event: RuntimeEvent) -> str:
    """Format a task diff output for review."""
    p = event.payload
    task_id = p.get("task_id", str(event.task_id or "unknown"))
    diff_text = p.get("diff", "")

    lines = [
        "========================================",
        f" Task Changes (Diff): {task_id}",
        "========================================",
    ]
    if not diff_text.strip():
        lines.append("  (No pending or uncommitted diff)")
    else:
        lines.append(diff_text)
    return "\n".join(lines)


def render_approval_prompt(
    approval_id: str,
    tool_id: str,
    reason: str,
    risk_level: str = "MEDIUM",
) -> str:
    """Render an interactive approval request prompt."""
    return (
        f"\n[APPROVAL REQUIRED - {risk_level}]\n"
        f"Action:       {tool_id}\n"
        f"Reason:       {reason}\n"
        f"Approval ID:  {approval_id}\n"
        f"Allow this operation? (y/n): "
    )


def render_report(task_id: str, state: str, plan_steps: list[str], diff: str) -> str:
    """Generate final execution report summary."""
    lines = [
        "========================================",
        f" Final Task Report: {task_id}",
        "========================================",
        f" Status: {state}",
        "\n Plan Steps:",
    ]
    for s in plan_steps:
        lines.append(f"   - {s}")
    lines.append("\n Modifications:")
    lines.append(f"   {diff if diff else 'No files modified'}")
    return "\n".join(lines)
