"""Scoped filesystem executor with workspace boundary enforcement (T041)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.execution.cancellation import CancellationToken
from coagent.execution.limits import DEFAULT_MAX_FILE_BYTES
from coagent.security import (
    ProtectedPathPolicy,
    WorkspaceEscapeError,
    require_path_within_workspace,
)
from coagent.tools.contracts import (
    ScopeEffect,
    ToolRequest,
    ToolResult,
    ToolResultStatus,
)
from coagent.tools.registry import ToolDefinition
from coagent.workspace import WorkspaceScope


class FilesystemExecutor:
    """Authorized executor for scoped filesystem operations."""

    def __init__(
        self,
        protected_path_policy: ProtectedPathPolicy | None = None,
        max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    ) -> None:
        self._policy = protected_path_policy or ProtectedPathPolicy()
        self._max_file_bytes = max_file_bytes

    def execute(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
        cancellation_token: CancellationToken | None = None,
    ) -> ToolResult:
        """Execute one authorized filesystem tool request."""
        if cancellation_token is not None and cancellation_token.is_cancelled:
            return self._cancelled_result(request, cancellation_token.reason)

        scope = WorkspaceScope(
            task_id=request.task_id,
            workspace_id=request.requested_scope.workspace_id,
            root=request.requested_scope.root,
        )

        try:
            tool_id = request.tool_id.lower()
            if "read" in tool_id:
                return self._handle_read(request, scope)
            if "write" in tool_id:
                return self._handle_write(request, scope)
            if "list" in tool_id:
                return self._handle_list(request, scope)
            if "delete" in tool_id:
                return self._handle_delete(request, scope)
            if "mkdir" in tool_id:
                return self._handle_mkdir(request, scope)

            raise ValueError(f"unsupported filesystem tool operation: {request.tool_id}")

        except WorkspaceEscapeError as exc:
            return self._error_result(
                request,
                code="FS_OUT_OF_SCOPE",
                message=str(exc),
                recoverability=Recoverability.NONE,
            )
        except PermissionError as exc:
            return self._error_result(
                request,
                code="FS_PERMISSION_DENIED",
                message=str(exc),
                recoverability=Recoverability.MANUAL,
            )
        except FileNotFoundError as exc:
            return self._error_result(
                request,
                code="FS_NOT_FOUND",
                message=str(exc),
                recoverability=Recoverability.AUTO,
            )
        except Exception as exc:
            return self._error_result(
                request,
                code="FS_OPERATION_FAILED",
                message=f"Filesystem operation failed: {exc}",
                recoverability=Recoverability.AUTO,
            )

    def _handle_read(self, request: ToolRequest, scope: WorkspaceScope) -> ToolResult:
        path_str = request.arguments.get("path")
        if not path_str or not isinstance(path_str, str):
            raise ValueError("Missing or invalid 'path' argument.")

        resolved = require_path_within_workspace(scope, path_str)
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path_str}")
        if resolved.is_dir():
            raise IsADirectoryError(f"Target is a directory, not a file: {path_str}")

        size = resolved.stat().st_size
        if size > self._max_file_bytes:
            raise ValueError(
                f"File size ({size} bytes) exceeds configured limit ({self._max_file_bytes} bytes)."
            )

        content = resolved.read_text(encoding="utf-8", errors="replace")
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "path": str(resolved.relative_to(Path(scope.root).resolve())),
                "content": content,
                "size_bytes": size,
            },
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )

    def _handle_write(self, request: ToolRequest, scope: WorkspaceScope) -> ToolResult:
        path_str = request.arguments.get("path")
        content = request.arguments.get("content")
        if not path_str or not isinstance(path_str, str):
            raise ValueError("Missing or invalid 'path' argument.")
        if content is None or not isinstance(content, str):
            raise ValueError("Missing or invalid 'content' argument.")

        self._check_protected_target(scope, path_str)
        resolved = require_path_within_workspace(scope, path_str)

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "path": str(resolved.relative_to(Path(scope.root).resolve())),
                "bytes_written": len(content.encode("utf-8")),
            },
            scope_effect=ScopeEffect.MODIFIED,
            created_at=datetime.now(UTC),
        )

    def _handle_list(self, request: ToolRequest, scope: WorkspaceScope) -> ToolResult:
        path_str = request.arguments.get("path", ".")
        if not isinstance(path_str, str):
            path_str = "."

        resolved = require_path_within_workspace(scope, path_str)
        if not resolved.exists():
            raise FileNotFoundError(f"Directory not found: {path_str}")
        if not resolved.is_dir():
            raise NotADirectoryError(f"Target is not a directory: {path_str}")

        entries: list[dict[str, Any]] = []
        root = Path(scope.root).resolve()
        for item in sorted(resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            entries.append(
                {
                    "name": item.name,
                    "path": str(item.relative_to(root)),
                    "is_directory": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else None,
                }
            )

        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "directory": str(resolved.relative_to(root)),
                "entries": entries,
            },
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )

    def _handle_delete(self, request: ToolRequest, scope: WorkspaceScope) -> ToolResult:
        path_str = request.arguments.get("path")
        if not path_str or not isinstance(path_str, str):
            raise ValueError("Missing or invalid 'path' argument.")

        self._check_protected_target(scope, path_str)
        resolved = require_path_within_workspace(scope, path_str)
        if not resolved.exists():
            raise FileNotFoundError(f"Target does not exist: {path_str}")

        if resolved.is_file():
            resolved.unlink()
        elif resolved.is_dir():
            resolved.rmdir()

        root = Path(scope.root).resolve()
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "path": str(resolved.relative_to(root)),
                "deleted": True,
            },
            scope_effect=ScopeEffect.MODIFIED,
            created_at=datetime.now(UTC),
        )

    def _handle_mkdir(self, request: ToolRequest, scope: WorkspaceScope) -> ToolResult:
        path_str = request.arguments.get("path")
        if not path_str or not isinstance(path_str, str):
            raise ValueError("Missing or invalid 'path' argument.")

        self._check_protected_target(scope, path_str)
        resolved = require_path_within_workspace(scope, path_str)
        resolved.mkdir(parents=True, exist_ok=True)

        root = Path(scope.root).resolve()
        return ToolResult(
            request_id=request.request_id,
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={
                "path": str(resolved.relative_to(root)),
                "created": True,
            },
            scope_effect=ScopeEffect.MODIFIED,
            created_at=datetime.now(UTC),
        )

    def _check_protected_target(self, scope: WorkspaceScope, path_str: str) -> None:
        category = self._policy.classify(scope, path_str)
        if category is not None:
            raise PermissionError(
                f"Cannot modify protected path '{path_str}' (category: {category.value})."
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
            category="FILESYSTEM",
            code=code,
            source="coagent.execution.filesystem",
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
            source="coagent.execution.filesystem",
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
