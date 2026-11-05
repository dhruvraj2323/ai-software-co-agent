"""Patch engine with dry-run validation, conflict detection, and rollback (T043, T044)."""

from __future__ import annotations

import difflib
import hashlib
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from coagent.security import (
    ProtectedPathPolicy,
    WorkspaceEscapeError,
    require_path_within_workspace,
)
from coagent.workspace import WorkspaceScope


class PatchOperationType(StrEnum):
    """Operation types supported in a patch."""

    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"


class PatchConflictError(RuntimeError):
    """Raised when patch application fails due to hash or content conflicts."""

    def __init__(self, code: str, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.path = path


class FilePatch(BaseModel):
    """Single file modification within a patch."""

    model_config = ConfigDict(extra="forbid")
    path: str = Field(min_length=1)
    operation: PatchOperationType
    base_hash: str | None = None  # Expected SHA-256 of target before modification
    content: str | None = None  # Full content for CREATE or full replacement MODIFY
    diff_hunks: list[str] | None = None  # Unified diff hunks for targeted changes


class Patch(BaseModel):
    """Multi-file atomic patch specification."""

    model_config = ConfigDict(extra="forbid")
    task_id: UUID
    expected_scope: list[str]  # Authorized file paths for this task
    file_patches: list[FilePatch]
    dry_run: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PatchApplyResult(BaseModel):
    """Outcome of applying or dry-running a patch."""

    model_config = ConfigDict(extra="forbid")
    success: bool
    dry_run: bool
    modified_files: list[str]
    diff: str
    error_code: str | None = None
    error_message: str | None = None


def compute_file_hash(path: Path) -> str:
    """Return SHA-256 hex digest of file contents."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class PatchEngine:
    """Deterministic patch applier with pre-flight conflict detection and user protection."""

    def __init__(
        self,
        protected_path_policy: ProtectedPathPolicy | None = None,
    ) -> None:
        self._policy = protected_path_policy or ProtectedPathPolicy()

    def validate(self, patch: Patch, scope: WorkspaceScope) -> None:
        """Validate patch against scope, protected paths, and base hashes."""
        expected_set = {Path(p).as_posix() for p in patch.expected_scope}

        for fp in patch.file_patches:
            norm_rel = Path(fp.path).as_posix()

            # Scope enforcement
            if expected_set and norm_rel not in expected_set:
                raise PatchConflictError(
                    code="PATCH_OUT_OF_SCOPE",
                    message=f"File '{norm_rel}' is not in the declared expected scope.",
                    path=norm_rel,
                )

            # Workspace containment
            try:
                resolved = require_path_within_workspace(scope, fp.path)
            except WorkspaceEscapeError as exc:
                raise PatchConflictError(
                    code="PATCH_WORKSPACE_ESCAPE",
                    message=str(exc),
                    path=norm_rel,
                ) from exc

            # Protected path check
            category = self._policy.classify(scope, fp.path)
            if category is not None:
                raise PatchConflictError(
                    code="PATCH_PROTECTED_PATH",
                    message=f"Cannot patch protected path '{norm_rel}' ({category.value}).",
                    path=norm_rel,
                )

            # Base hash and existence checks
            if fp.operation is PatchOperationType.CREATE:
                if resolved.exists():
                    raise PatchConflictError(
                        code="PATCH_ALREADY_EXISTS",
                        message=f"File already exists: {norm_rel}",
                        path=norm_rel,
                    )
            elif fp.operation in (PatchOperationType.MODIFY, PatchOperationType.DELETE):
                if not resolved.exists():
                    raise PatchConflictError(
                        code="PATCH_FILE_NOT_FOUND",
                        message=f"Target file does not exist: {norm_rel}",
                        path=norm_rel,
                    )
                if resolved.is_dir():
                    raise PatchConflictError(
                        code="PATCH_TARGET_IS_DIRECTORY",
                        message=f"Target is a directory: {norm_rel}",
                        path=norm_rel,
                    )

                if fp.base_hash is not None:
                    actual_hash = compute_file_hash(resolved)
                    if actual_hash != fp.base_hash:
                        raise PatchConflictError(
                            code="PATCH_STALE_HASH",
                            message=(
                                f"Base hash mismatch for '{norm_rel}'. "
                                f"Expected {fp.base_hash[:8]}..., found {actual_hash[:8]}... "
                                "File was modified since plan context was captured."
                            ),
                            path=norm_rel,
                        )

    def apply(self, patch: Patch, scope: WorkspaceScope) -> PatchApplyResult:
        """Atomically apply or dry-run a patch with rollback on error."""
        try:
            self.validate(patch, scope)
        except PatchConflictError as exc:
            return PatchApplyResult(
                success=False,
                dry_run=patch.dry_run,
                modified_files=[],
                diff="",
                error_code=exc.code,
                error_message=str(exc),
            )

        root = Path(scope.root).resolve()
        diff_lines: list[str] = []
        backups: dict[Path, str | None] = {}
        modified: list[str] = []

        try:
            for fp in patch.file_patches:
                resolved = require_path_within_workspace(scope, fp.path)
                rel_path = resolved.relative_to(root).as_posix()

                old_content = (
                    resolved.read_text(encoding="utf-8", errors="replace")
                    if resolved.exists()
                    else ""
                )
                new_content = ""

                if fp.operation is PatchOperationType.CREATE:
                    new_content = fp.content or ""
                elif fp.operation is PatchOperationType.DELETE:
                    new_content = ""
                elif fp.operation is PatchOperationType.MODIFY:
                    new_content = fp.content if fp.content is not None else old_content

                # Generate unified diff
                patch_diff = difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f"a/{rel_path}",
                    tofile=f"b/{rel_path}",
                )
                diff_lines.extend(patch_diff)

                if not patch.dry_run:
                    # Save backup for rollback
                    backups[resolved] = old_content if resolved.exists() else None

                    if fp.operation in (PatchOperationType.CREATE, PatchOperationType.MODIFY):
                        resolved.parent.mkdir(parents=True, exist_ok=True)
                        resolved.write_text(new_content, encoding="utf-8")
                    elif fp.operation is PatchOperationType.DELETE:
                        if resolved.exists():
                            resolved.unlink()

                    modified.append(rel_path)

            return PatchApplyResult(
                success=True,
                dry_run=patch.dry_run,
                modified_files=modified
                if not patch.dry_run
                else [fp.path for fp in patch.file_patches],
                diff="".join(diff_lines),
            )

        except Exception as exc:
            # Atomic rollback on any failure
            for path, prev_content in backups.items():
                if prev_content is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.write_text(prev_content, encoding="utf-8")

            return PatchApplyResult(
                success=False,
                dry_run=patch.dry_run,
                modified_files=[],
                diff="",
                error_code="PATCH_APPLICATION_ERROR",
                error_message=f"Application failed and was rolled back: {exc}",
            )
