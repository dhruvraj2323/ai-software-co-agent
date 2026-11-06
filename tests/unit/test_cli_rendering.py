"""Unit tests for CLI presentation and rendering utilities (T095)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from coagent_cli.rendering import (
    render_approval_prompt,
    render_diff,
    render_plan,
    render_report,
    render_task_status,
)

from coagent.core.types import EventSeverity
from coagent.protocol.messages import (
    PROTOCOL_VERSION,
    EventType,
    RuntimeEvent,
)


def make_test_event(event_type: EventType, payload: dict) -> RuntimeEvent:
    return RuntimeEvent(
        protocol_version=PROTOCOL_VERSION,
        event_id=uuid4(),
        session_id=uuid4(),
        task_id=uuid4(),
        type=event_type,
        payload=payload,
        severity=EventSeverity.INFO,
        created_at=datetime.now(UTC),
    )


def test_render_task_status() -> None:
    event = make_test_event(
        EventType.TASK_STATE_CHANGED,
        {"task_id": "task-abc", "state": "READY", "goal": "Implement feature"},
    )
    rendered = render_task_status(event)
    assert "Task Status: task-abc" in rendered
    assert "State:      READY" in rendered
    assert "Goal:       Implement feature" in rendered


def test_render_plan() -> None:
    event = make_test_event(
        EventType.PLAN_UPDATED,
        {
            "task_id": "task-xyz",
            "state": "READY",
            "plan": [
                {"step": 1, "description": "Inspect repository files"},
                {"step": 2, "description": "Apply edits"},
            ],
        },
    )
    rendered = render_plan(event)
    assert "Task Plan: task-xyz [READY]" in rendered
    assert "[1] Inspect repository files" in rendered
    assert "[2] Apply edits" in rendered


def test_render_diff() -> None:
    event = make_test_event(
        EventType.CONTEXT_UPDATED,
        {"task_id": "task-1", "diff": "--- a/src.py\n+++ b/src.py\n@@ -1 +1 @@\n+print('hi')"},
    )
    rendered = render_diff(event)
    assert "Task Changes (Diff): task-1" in rendered
    assert "+print('hi')" in rendered


def test_render_approval_prompt() -> None:
    prompt = render_approval_prompt(
        approval_id="app-999",
        tool_id="workspace.write_file",
        reason="Overwriting configuration file",
        risk_level="HIGH",
    )
    assert "[APPROVAL REQUIRED - HIGH]" in prompt
    assert "workspace.write_file" in prompt
    assert "app-999" in prompt


def test_render_report() -> None:
    report = render_report(
        task_id="task-42",
        state="COMPLETE",
        plan_steps=["Step 1", "Step 2"],
        diff="modified: file.txt",
    )
    assert "Final Task Report: task-42" in report
    assert "Status: COMPLETE" in report
    assert "Step 1" in report
    assert "modified: file.txt" in report
