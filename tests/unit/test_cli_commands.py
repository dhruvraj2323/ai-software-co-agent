"""Unit tests for CLI commands and argument parser (T095)."""

from __future__ import annotations

from uuid import uuid4

from coagent_cli.client import RuntimeClient
from coagent_cli.main import run_cli

from coagent.runtime.service import RuntimeService


def test_cli_plan_command() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    code = run_cli(["plan", "Implement caching subsystem"], client=client)
    assert code == 0


def test_cli_run_command() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    code = run_cli(["run", "Build parser module"], client=client)
    assert code == 0


def test_cli_status_and_cancel_command() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    # 1. Create task first
    task_evt = client.create_task("Sample task")
    task_id = str(task_evt.task_id)

    # 2. Check status via CLI
    status_code = run_cli(["status", task_id], client=client)
    assert status_code == 0

    # 3. Check diff via CLI
    diff_code = run_cli(["diff", task_id], client=client)
    assert diff_code == 0

    # 4. Cancel via CLI
    cancel_code = run_cli(["cancel", task_id, "--reason", "Test cancellation"], client=client)
    assert cancel_code == 0


def test_cli_approve_command() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    task_evt = client.create_task("Approval task")
    task_id = str(task_evt.task_id)

    # Approve
    code = run_cli(["approve", task_id, "app-001"], client=client)
    assert code == 0

    # Deny
    deny_code = run_cli(["approve", task_id, "app-002", "--deny"], client=client)
    assert deny_code == 0


def test_cli_health_and_config() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    assert run_cli(["health"], client=client) == 0
    assert run_cli(["config"], client=client) == 0


def test_cli_handles_invalid_task_uuid() -> None:
    service = RuntimeService()
    client = RuntimeClient(service=service)

    # Bad UUID
    code = run_cli(["status", "not-a-uuid"], client=client)
    assert code != 0

    # Non-existent UUID
    code2 = run_cli(["status", str(uuid4())], client=client)
    assert code2 != 0
