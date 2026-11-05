"""Controlled execution runner for validation gates (TVS-001 §16)."""

from __future__ import annotations

import subprocess
import time
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.execution.process import sanitize_process_environment
from coagent.security.path import require_path_within_workspace
from coagent.validation.evidence import GateCategory, GateStatus, ValidationResult
from coagent.workspace.scope import WorkspaceScope


class ValidationGateDefinition(BaseModel):
    """Specification of an executable validation gate."""

    model_config = ConfigDict(extra="forbid")

    gate_id: str
    command: list[str]
    category: GateCategory = GateCategory.UNIT
    timeout_seconds: float = Field(default=60.0, ge=1.0)
    required: bool = True


class ValidationExecutor(Protocol):
    """Protocol for custom validation process executors."""

    def execute(
        self,
        command: list[str],
        cwd: str,
        timeout_seconds: float,
    ) -> Any: ...


class ValidationRunner:
    """Executes validation gates within controlled boundaries and produces immutable evidence."""

    def __init__(
        self,
        executor: ValidationExecutor | None = None,
    ) -> None:
        self._executor = executor

    def run_gate(
        self,
        gate: ValidationGateDefinition,
        task_id: UUID,
        scope: WorkspaceScope,
        source_version: str | None = None,
    ) -> ValidationResult:
        """Execute a validation command strictly within the authorized workspace scope."""
        start_time = time.perf_counter()
        cmd_str = " ".join(gate.command)

        try:
            resolved_cwd = require_path_within_workspace(scope, ".")

            if self._executor is not None:
                proc_result = self._executor.execute(
                    command=gate.command,
                    cwd=str(resolved_cwd),
                    timeout_seconds=gate.timeout_seconds,
                )
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                exit_code = getattr(proc_result, "exit_code", 0)
                timed_out = getattr(proc_result, "timed_out", False)
                cancelled = getattr(proc_result, "cancelled", False)
                stdout = getattr(proc_result, "stdout", "")
                stderr = getattr(proc_result, "stderr", "")

                if timed_out:
                    status = GateStatus.TIMEOUT
                elif cancelled:
                    status = GateStatus.BLOCKED
                elif exit_code == 0:
                    status = GateStatus.PASS
                else:
                    status = GateStatus.FAIL

                return ValidationResult(
                    gate_id=gate.gate_id,
                    task_id=task_id,
                    command=cmd_str,
                    status=status,
                    exit_code=exit_code,
                    duration_ms=duration_ms,
                    source_version=source_version,
                    stdout_summary=stdout[:500] if stdout else None,
                    stderr_summary=stderr[:500] if stderr else None,
                )

            env = sanitize_process_environment()
            proc = subprocess.run(
                gate.command,
                cwd=str(resolved_cwd),
                env=env,
                capture_output=True,
                text=True,
                timeout=gate.timeout_seconds,
            )
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            status = GateStatus.PASS if proc.returncode == 0 else GateStatus.FAIL
            return ValidationResult(
                gate_id=gate.gate_id,
                task_id=task_id,
                command=cmd_str,
                status=status,
                exit_code=proc.returncode,
                duration_ms=duration_ms,
                source_version=source_version,
                stdout_summary=proc.stdout[:500] if proc.stdout else None,
                stderr_summary=proc.stderr[:500] if proc.stderr else None,
            )

        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            raw_out = exc.stdout or ""
            out = raw_out if isinstance(raw_out, str) else raw_out.decode()
            raw_err = exc.stderr or ""
            err = raw_err if isinstance(raw_err, str) else raw_err.decode()
            return ValidationResult(
                gate_id=gate.gate_id,
                task_id=task_id,
                command=cmd_str,
                status=GateStatus.TIMEOUT,
                exit_code=None,
                duration_ms=duration_ms,
                source_version=source_version,
                stdout_summary=out[:500] if out else None,
                stderr_summary=err[:500] if err else f"Timed out after {gate.timeout_seconds}s",
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return ValidationResult(
                gate_id=gate.gate_id,
                task_id=task_id,
                command=cmd_str,
                status=GateStatus.BLOCKED,
                exit_code=None,
                duration_ms=duration_ms,
                source_version=source_version,
                stderr_summary=f"Validation execution blocked: {exc}",
            )
