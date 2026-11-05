"""Filesystem artifact store with integrity verification and path containment (T089)."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from coagent.artifacts.models import ArtifactReference
from coagent.security.path import WorkspaceEscapeError


class ArtifactStoreError(RuntimeError):
    """Base exception for artifact store failures."""


class ArtifactIntegrityError(ArtifactStoreError):
    """Raised when an artifact's cryptographic hash does not match its stored content."""


_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9_.-]")


def _sanitize_filename(name: str) -> str:
    """Sanitize artifact filename to prevent directory traversal or invalid characters."""
    base = os.path.basename(name)
    sanitized = _UNSAFE_FILENAME_CHARS.sub("_", base).strip("._")
    return sanitized if sanitized else "artifact"


class ArtifactStore:
    """Content-addressable, filesystem-backed store for offloaded task artifacts (T089)."""

    def __init__(self, root_dir: Path | str) -> None:
        self._root_dir = Path(root_dir).resolve()
        self._root_dir.mkdir(parents=True, exist_ok=True)

    @property
    def root_dir(self) -> Path:
        """Root directory hosting artifact files."""
        return self._root_dir

    def _resolve_artifact_path(self, task_id: UUID, artifact_id: UUID, safe_name: str) -> Path:
        """Resolve and validate that the artifact path stays strictly inside root_dir."""
        task_dir = (self._root_dir / str(task_id)).resolve()
        try:
            task_dir.relative_to(self._root_dir)
        except ValueError as exc:
            raise WorkspaceEscapeError(
                f"Artifact path '{task_dir}' escapes artifact root '{self._root_dir}'."
            ) from exc

        task_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{artifact_id}_{safe_name}"
        full_path = (task_dir / filename).resolve()

        try:
            full_path.relative_to(self._root_dir)
        except ValueError as exc:
            raise WorkspaceEscapeError(
                f"Artifact filename '{filename}' escapes artifact root."
            ) from exc

        return full_path

    def store_bytes(
        self,
        task_id: UUID,
        name: str,
        content: bytes,
        media_type: str = "application/octet-stream",
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactReference:
        """Persist raw byte content and return an immutable reference with SHA-256 hash."""
        artifact_id = uuid4()
        safe_name = _sanitize_filename(name)
        target_path = self._resolve_artifact_path(task_id, artifact_id, safe_name)

        sha256 = hashlib.sha256(content).hexdigest()
        size_bytes = len(content)

        target_path.write_bytes(content)

        # Store relative storage path to stay portable across environments
        storage_rel_path = target_path.relative_to(self._root_dir).as_posix()

        return ArtifactReference(
            artifact_id=artifact_id,
            task_id=task_id,
            name=name,
            media_type=media_type,
            sha256_hash=sha256,
            size_bytes=size_bytes,
            storage_path=storage_rel_path,
            metadata=metadata or {},
        )

    def store_text(
        self,
        task_id: UUID,
        name: str,
        content: str,
        media_type: str = "text/plain",
        metadata: dict[str, Any] | None = None,
        encoding: str = "utf-8",
    ) -> ArtifactReference:
        """Persist string content as encoded text and return an immutable reference."""
        data = content.encode(encoding)
        return self.store_bytes(
            task_id=task_id,
            name=name,
            content=data,
            media_type=media_type,
            metadata=metadata,
        )

    def _get_absolute_path(self, reference: ArtifactReference) -> Path:
        """Resolve storage_path on the reference against root_dir and check bounds."""
        resolved = (self._root_dir / reference.storage_path).resolve()
        try:
            resolved.relative_to(self._root_dir)
        except ValueError as exc:
            raise WorkspaceEscapeError(
                f"Artifact reference path '{reference.storage_path}' escapes root."
            ) from exc
        return resolved

    def retrieve_bytes(
        self,
        reference: ArtifactReference,
        verify_integrity: bool = True,
    ) -> bytes:
        """Retrieve stored artifact bytes with optional cryptographic integrity verification."""
        path = self._get_absolute_path(reference)
        if not path.is_file():
            raise FileNotFoundError(f"Artifact not found at storage path: {reference.storage_path}")

        data = path.read_bytes()
        if verify_integrity:
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != reference.sha256_hash:
                raise ArtifactIntegrityError(
                    f"Integrity check failed for artifact '{reference.artifact_id}'. "
                    f"Expected SHA-256 {reference.sha256_hash}, got {actual_hash}."
                )
        return data

    def retrieve_text(
        self,
        reference: ArtifactReference,
        verify_integrity: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """Retrieve and decode stored text artifact."""
        raw = self.retrieve_bytes(reference, verify_integrity=verify_integrity)
        return raw.decode(encoding)

    def exists(self, reference: ArtifactReference) -> bool:
        """Return True if the referenced artifact file exists within storage."""
        try:
            path = self._get_absolute_path(reference)
            return path.is_file()
        except (WorkspaceEscapeError, ValueError):
            return False
