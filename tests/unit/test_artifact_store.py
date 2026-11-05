"""Unit tests for ArtifactStore and ArtifactReference (T089)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.artifacts.store import ArtifactIntegrityError, ArtifactStore
from coagent.security.path import WorkspaceEscapeError


def test_artifact_store_stores_and_retrieves_text(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()
    content = "Large test output summary log\nLine 2\nLine 3"

    ref = store.store_text(
        task_id=task_id,
        name="test_output.log",
        content=content,
        media_type="text/plain",
        metadata={"step": "validation"},
    )

    assert ref.task_id == task_id
    assert ref.name == "test_output.log"
    assert ref.media_type == "text/plain"
    assert ref.size_bytes == len(content.encode("utf-8"))
    assert ref.sha256_hash == hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert ref.metadata == {"step": "validation"}

    # Retrieve and check content
    retrieved = store.retrieve_text(ref)
    assert retrieved == content
    assert store.exists(ref) is True


def test_artifact_store_stores_and_retrieves_bytes(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()
    data = b"\x00\x01\x02\x03\x04\xff"

    ref = store.store_bytes(
        task_id=task_id,
        name="binary_artifact.bin",
        content=data,
        media_type="application/octet-stream",
    )

    assert ref.size_bytes == 6
    assert store.retrieve_bytes(ref) == data


def test_artifact_store_detects_tampered_content(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()
    content = "Original authentic content"

    ref = store.store_text(task_id=task_id, name="evidence.txt", content=content)

    # Tamper with the physical file on disk
    file_path = store.root_dir / ref.storage_path
    file_path.write_text("Tampered malicious content", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ArtifactIntegrityError, match="Integrity check failed"):
        store.retrieve_text(ref, verify_integrity=True)

    # Should succeed when verification is bypassed
    assert store.retrieve_text(ref, verify_integrity=False) == "Tampered malicious content"


def test_artifact_store_sanitizes_path_traversal(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()

    # Attempt to write outside using relative traversal
    ref = store.store_text(
        task_id=task_id,
        name="../../etc/shadow",
        content="secret",
    )

    # Filename should be sanitized to stay inside the task directory
    assert ".." not in ref.storage_path
    assert store.exists(ref) is True
    file_path = store.root_dir / ref.storage_path
    assert file_path.is_file()
    assert str(tmp_path / "artifacts") in str(file_path.resolve())


def test_artifact_store_blocks_escaped_reference(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()
    ref = store.store_text(task_id=task_id, name="safe.txt", content="safe")

    # Manually tamper storage_path on reference to point outside root
    corrupted_ref = ref.model_copy(update={"storage_path": "../../outside.txt"})

    with pytest.raises(WorkspaceEscapeError):
        store.retrieve_text(corrupted_ref)
