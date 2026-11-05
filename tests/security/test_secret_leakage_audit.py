"""Adversarial secret leakage tests for audit and event subsystem (T093)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from coagent.artifacts.store import ArtifactStore
from coagent.audit.recorder import AuditRecorder
from coagent.audit.redaction import OutputRedactor, SecretLeakageError
from coagent.audit.trace import TaskTraceReconstructor
from coagent.core.events import EventType


def test_adversarial_tool_output_leakage_blocked(tmp_path: Path) -> None:
    """Ensure sensitive credentials in tool outputs or error messages never leak to disk."""
    log_file = tmp_path / "audit_secure.jsonl"
    recorder = AuditRecorder(log_path=log_file)
    task_id = uuid4()
    session_id = uuid4()

    # Construct test secrets via concatenation
    simulated_token = "ghp_" + "ADVERSARIAL1234567890abcdef"
    simulated_key = "AKIA" + "1234567890ABCDEF"
    simulated_password = "MySuperSecretPassword99!"
    dynamic_secret = "CustomSecretPhraseXYZ"
    recorder._redactor.add_secret(dynamic_secret)

    # 1. Record event containing simulated secret values
    recorder.record_task_event(
        task_id=task_id,
        session_id=session_id,
        event_type=EventType.TOOL_EXECUTED,
        payload={
            "command": f"curl -H 'Authorization: Bearer {simulated_token}'",
            "env": {"AWS_ACCESS": simulated_key},
            "credentials": {"password": simulated_password},
            "extra": dynamic_secret,
        },
    )

    # 2. Verify disk contents do not contain any plaintext secret
    assert log_file.exists()
    disk_content = log_file.read_text(encoding="utf-8")

    assert simulated_token not in disk_content
    assert simulated_key not in disk_content
    assert simulated_password not in disk_content
    assert dynamic_secret not in disk_content

    # 3. Verify reconstructed TaskTrace contains no plaintext secret
    reconstructor = TaskTraceReconstructor(recorder)
    trace = reconstructor.reconstruct(task_id)
    trace_dict = trace.model_dump()
    trace_str = str(trace_dict)

    assert simulated_token not in trace_str
    assert simulated_key not in trace_str
    assert simulated_password not in trace_str


def test_artifact_store_path_traversal_adversarial(tmp_path: Path) -> None:
    """Ensure attacker cannot read or overwrite system files using crafted artifact references."""
    store = ArtifactStore(tmp_path / "artifacts")
    task_id = uuid4()

    # Attempt to write outside storage
    adversarial_names = [
        "../../../windows/win.ini",
        "..\\..\\sensitive.txt",
        "/etc/passwd",
        "nested/../../escape.log",
    ]

    for evil_name in adversarial_names:
        ref = store.store_text(task_id=task_id, name=evil_name, content="safe_content")
        # Assert the resulting file is strictly inside tmp_path / artifacts
        full_path = (store.root_dir / ref.storage_path).resolve()
        assert full_path.is_relative_to(store.root_dir)


def test_redactor_raises_on_unredacted_leakage_assertion() -> None:
    """Verify redactor assert_clean catches leakage."""
    redactor = OutputRedactor()
    leaked_token = "ghp_" + "UNREDACTEDTOKEN123456789"

    with pytest.raises(SecretLeakageError):
        redactor.assert_clean(f"Status report: {leaked_token}")
