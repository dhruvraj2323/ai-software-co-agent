"""Main CLI entrypoint for AI Software Co-Agent (T095)."""

from __future__ import annotations

import argparse
import sys
from uuid import UUID

from coagent_cli.client import RuntimeClient, RuntimeClientError
from coagent_cli.commands.config import get_default_config
from coagent_cli.commands.run import run_task_cmd
from coagent_cli.commands.task import cancel_task_cmd, create_task_cmd
from coagent_cli.rendering import render_diff, render_plan, render_task_status


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI command argument parser."""
    parser = argparse.ArgumentParser(
        prog="coagent",
        description="AI Software Co-Agent CLI runtime client",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # plan
    plan_parser = subparsers.add_parser("plan", help="Inspect requirement and generate plan")
    plan_parser.add_argument("goal", type=str, help="Task engineering goal")

    # run
    run_parser = subparsers.add_parser("run", help="Execute the controlled engineering loop")
    run_parser.add_argument("goal", type=str, help="Task engineering goal")

    # status
    status_parser = subparsers.add_parser("status", help="Show task state and current stage")
    status_parser.add_argument("task_id", type=str, help="Target task UUID")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Show actual task diff")
    diff_parser.add_argument("task_id", type=str, help="Target task UUID")

    # cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an active task")
    cancel_parser.add_argument("task_id", type=str, help="Target task UUID")
    cancel_parser.add_argument("--reason", type=str, default="Cancelled by user via CLI")

    # approve
    approve_parser = subparsers.add_parser("approve", help="Respond to an approval request")
    approve_parser.add_argument("task_id", type=str, help="Target task UUID")
    approve_parser.add_argument("approval_id", type=str, help="Approval ID")
    approve_parser.add_argument("--deny", action="store_true", help="Deny instead of allow")
    approve_parser.add_argument("--reason", type=str, default="")

    # config
    subparsers.add_parser("config", help="Show client configuration")

    # health
    subparsers.add_parser("health", help="Check runtime health")

    return parser


def run_cli(args: list[str] | None = None, client: RuntimeClient | None = None) -> int:
    """Execute CLI commands and return exit code."""
    parser = build_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    cli_client = client or RuntimeClient()

    try:
        if parsed.command == "plan":
            create_task_cmd(cli_client, goal=parsed.goal)
            plan_evt = cli_client.request_plan()
            print(render_plan(plan_evt))
            return 0

        if parsed.command == "run":
            out = run_task_cmd(cli_client, goal=parsed.goal)
            print(out)
            return 0

        if parsed.command == "status":
            evt = cli_client.get_status(task_id=UUID(parsed.task_id))
            print(render_task_status(evt))
            return 0

        if parsed.command == "diff":
            evt = cli_client.get_diff(task_id=UUID(parsed.task_id))
            print(render_diff(evt))
            return 0

        if parsed.command == "cancel":
            out = cancel_task_cmd(cli_client, parsed.task_id, reason=parsed.reason)
            print(out)
            return 0

        if parsed.command == "approve":
            approved = not parsed.deny
            evt = cli_client.respond_approval(
                task_id=UUID(parsed.task_id),
                approval_id=parsed.approval_id,
                approved=approved,
                reason=parsed.reason,
            )
            print(render_task_status(evt))
            return 0

        if parsed.command == "config":
            import json
            print(json.dumps(get_default_config(), indent=2))
            return 0

        if parsed.command == "health":
            health_info = cli_client._service.health()
            print(f"Runtime Status: {health_info['status']} (v{health_info['protocol_version']})")
            return 0

    except RuntimeClientError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2

    return 0


def main() -> None:
    """Console script entrypoint."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
