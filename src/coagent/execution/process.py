"""Bounded process and PowerShell executor with resource controls (T042, T046, T048)."""

from __future__ import annotations

import os
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.execution.cancellation import CancellationToken
from coagent.execution.limits import (
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_PROCESS_TIMEOUT_SECONDS,
)
from coagent.security.path import (
    WorkspaceEscapeError,
    require_path_within_workspace,
)
from coagent.security.secrets import SecretRedactor
from coagent.tools.contracts import (
    ScopeEffect,
    ToolRequest,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.registry import ToolDefinition
from coagent.workspace import WorkspaceScope

# Environment variables that should be sanitized or stripped for child processes
_SENSITIVE_ENV_PATTERN = re.compile(
    r"(?i)(key|token|secret|password|passwd|auth|credential|cert|private)",
)
_SAFE_SYSTEM_VARS = {
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "HOMEDRIVE",
    "HOMEPATH",
    "LANG",
    "LC_ALL",
}


def sanitize_process_environment(
    base_env: dict[str, str] | None = None,
    allow_vars: set[str] | None = None,
) -> dict[str, str]:
    """Return a sanitized copy of environment variables, stripping potential secrets."""
    source = dict(base_env if base_env is not None else os.environ)
    safe_names = _SAFE_SYSTEM_VARS | (allow_vars or set())

    sanitized: dict[str, str] = {}
    for key, value in source.items():
        if key in safe_names:
            sanitized[key] = value
        elif not _SENSITIVE_ENV_PATTERN.search(key):
            sanitized[key] = value

    return sanitized


class ProcessExecutor:
    """Bounded executor for shell commands, PowerShell, and child processes."""

    def __init__(
        self,
        default_timeout_seconds: float = DEFAULT_PROCESS_TIMEOUT_SECONDS,
        max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
        secret_redactor: SecretRedactor | None = None,
    ) -> None:
        self._default_timeout = default_timeout_seconds
        self._max_output_bytes = max_output_bytes
        self._redactor = secret_redactor or SecretRedactor()

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
        cancellation_token: CancellationToken | None = None,
    ) -> ToolResult:
        """Execute one authorized process tool request under strict limits."""
        if cancellation_token is not None and cancellation_token.is_cancelled:
            return self._cancelled_result(request, cancellation_token.reason)

        scope = WorkspaceScope(
            task_id=request.task_id,
            workspace_id=request.requested_scope.workspace_id,
            root=request.requested_scope.root,
        )

        try:
            cwd_arg = request.arguments.get("cwd", ".")
            if not isinstance(cwd_arg, str):
                cwd_arg = "."

            resolved_cwd = require_path_within_workspace(scope, cwd_arg)
            if not resolved_cwd.exists() or not resolved_cwd.is_dir():
                raise FileNotFoundError(f"Working directory does not exist: {cwd_arg}")

            cmd = request.arguments.get("command")
            if not cmd or not isinstance(cmd, str):
                raise ValueError("Missing or invalid 'command' argument.")

            timeout = float(request.arguments.get("timeout_seconds", self._default_timeout))

            # Determine shell / command invocation
            tool_id = request.tool_id.lower()
            if "powershell" in tool_id:
                args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd]
            else:
                args = cmd

            return self._run_subprocess(
                request=request,
                args=args,
                cwd=resolved_cwd,
                timeout=timeout,
                cancellation_token=cancellation_token,
            )

        except WorkspaceEscapeError as exc:
            return self._error_result(
                request,
                code="PROC_OUT_OF_SCOPE",
                message=str(exc),
                recoverability=Recoverability.NONE,
            )
        except Exception as exc:
            return self._error_result(
                request,
                code="PROC_EXECUTION_FAILED",
                message=f"Process execution failed: {exc}",
                recoverability=Recoverability.AUTO,
            )

    def _run_subprocess(
        self,
        request: ToolRequest,
        args: list[str] | str,
        cwd: Path,
        timeout: float,
        cancellation_token: CancellationToken | None,
    ) -> ToolResult:
        env = sanitize_process_environment()
        start_time = time.monotonic()
        use_shell = isinstance(args, str)

        try:
            process = subprocess.Popen(
                args,
                cwd=str(cwd),
                env=env,
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
            )
        except Exception as exc:
            return self._error_result(
                request,
                code="PROC_SPAWN_FAILED",
                message=f"Failed to spawn process: {exc}",
                recoverability=Recoverability.AUTO,
            )

        stdout_bytes = b""
        stderr_bytes = b""
        timed_out = False
        cancelled = False

        try:
            while True:
                if cancellation_token is not None and cancellation_token.is_cancelled:
                    cancelled = True
                    process.kill()
                    out, err = process.communicate()
                    stdout_bytes = out or b""
                    stderr_bytes = err or b""
                    break

                elapsed = time.monotonic() - start_time
                if elapsed > timeout:
                    timed_out = True
                    process.kill()
                    out, err = process.communicate()
                    stdout_bytes = out or b""
                    stderr_bytes = err or b""
                    break

                step_timeout = min(0.2, max(0.01, timeout - elapsed))
                try:
                    out, err = process.communicate(timeout=step_timeout)
                    stdout_bytes = out or b""
                    stderr_bytes = err or b""
                    break
                except subprocess.TimeoutExpired:
                    continue

        except Exception as exc:
            process.kill()
            return self._error_result(
                request,
                code="PROC_EXECUTION_ERROR",
                message=str(exc),
                recoverability=Recoverability.AUTO,
            )

        duration_ms = int((time.monotonic() - start_time) * 1000)

        if cancelled:
            return self._cancelled_result(
                request,
                cancellation_token.reason if cancellation_token else "Process cancelled.",
            )

        if timed_out:
            return self._error_result(
                request,
                code="PROC_TIMEOUT",
                message=f"Process timed out after {timeout} seconds.",
                recoverability=Recoverability.AUTO,
            )

        # Enforce output buffer limits
        truncated = False
        total_len = len(stdout_bytes) + len(stderr_bytes)
        if total_len > self._max_output_bytes:
            truncated = True
            stdout_bytes = stdout_bytes[: self._max_output_bytes // 2]
            stderr_bytes = stderr_bytes[: self._max_output_bytes // 2]

        stdout_text = self._redactor.redact(stdout_bytes.decode("utf-8", errors="replace"))
        stderr_text = self._redactor.redact(stderr_bytes.decode("utf-8", errors="replace"))
        exit_code = process.returncode if process.returncode is not None else -1

        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "exit_code": exit_code,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "duration_ms": duration_ms,
                "truncated": truncated,
            },
            exit_code=exit_code,
            duration_ms=duration_ms,
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )

    def _error_result(
        self,
        request: ToolRequest,
        *,
        code: str,
        message: str,
        recoverability: Recoverability,
    ) -> ToolResult:
        now = datetime.now(UTC)
        error = ErrorRecord(
            error_id=uuid4(),
            task_id=request.task_id,
            correlation_id=request.correlation_id,
            category="PROCESS",
            code=code,
            source="coagent.execution.process",
            message=message,
            severity=EventSeverity.ERROR,
            recoverability=recoverability,
            evidence_refs=[],
            occurred_at=now,
            normalized_at=now,
        )
        return ToolResult(
            request_id=request.request_id,
            success=False,
            status=ToolResultStatus.FAILED,
            error=error,
            scope_effect=ScopeEffect.NONE,
            created_at=now,
        )

    def _cancelled_result(self, request: ToolRequest, reason: str | None) -> ToolResult:
        now = datetime.now(UTC)
        error = ErrorRecord(
            error_id=uuid4(),
            task_id=request.task_id,
            correlation_id=request.correlation_id,
            category="EXECUTION",
            code="OPERATION_CANCELLED",
            source="coagent.execution.process",
            message=reason or "Operation cancelled.",
            severity=EventSeverity.WARNING,
            recoverability=Recoverability.MANUAL,
            occurred_at=now,
            normalized_at=now,
        )
        return ToolResult(
            request_id=request.request_id,
            success=False,
            status=ToolResultStatus.CANCELLED,
            error=error,
            scope_effect=ScopeEffect.NONE,
            created_at=now,
        )
