"""Unit tests for OutputRedactor (T090)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from coagent.audit.redaction import OutputRedactor, SecretLeakageError
from coagent.core.events import EventEnvelope, EventType


def test_redact_built_in_secrets() -> None:
    redactor = OutputRedactor()

    # Construct test secrets via concatenation to avoid static CI scanner alerts
    gh_token = "ghp_" + "ABCDEF1234567890abcdefghij"
    aws_key = "AKIA" + "IOSFODNN7EXAMPLE"

    text = f"Token is {gh_token} and AWS key is {aws_key}."
    redacted = redactor.redact_text(text)

    assert gh_token not in redacted
    assert aws_key not in redacted
    assert "[REDACTED]" in redacted


def test_redact_nested_structures() -> None:
    redactor = OutputRedactor()
    test_secret = "ghp_" + "123456789012345678901234567890"

    data = {
        "user": "developer",
        "tokens": [test_secret, "normal_value"],
        "nested": {
            "auth": f"Bearer {test_secret}",
        },
    }

    clean = redactor.redact_value(data)

    assert test_secret not in str(clean)
    assert clean["user"] == "developer"
    assert clean["tokens"][0] == "[REDACTED]"
    assert clean["tokens"][1] == "normal_value"
    assert "[REDACTED]" in clean["nested"]["auth"]


def test_redact_event_envelope() -> None:
    redactor = OutputRedactor()
    test_secret = "ghp_" + "SECRET1234567890ABCDEF"

    event = EventEnvelope.create(
        event_type=EventType.TOOL_EXECUTED,
        task_id=uuid4(),
        session_id=uuid4(),
        payload={"command": f"curl -H 'Authorization: Bearer {test_secret}'"},
        source=f"runner-{test_secret}",
    )

    clean_event = redactor.redact_event(event)

    assert test_secret not in str(clean_event.payload)
    assert test_secret not in clean_event.source
    assert "[REDACTED]" in str(clean_event.payload)
    assert "[REDACTED]" in clean_event.source


def test_redact_dynamic_registered_secret() -> None:
    redactor = OutputRedactor()
    dynamic_password = "SuperSecretPassword123!"
    redactor.add_secret(dynamic_password)

    text = f"Connecting with password: {dynamic_password}"
    clean = redactor.redact_text(text)

    assert dynamic_password not in clean
    assert "[REDACTED]" in clean


def test_assert_clean_validation() -> None:
    redactor = OutputRedactor()
    test_secret = "ghp_" + "MYTOKEN1234567890abcdef"

    # Should raise for dirty text
    with pytest.raises(SecretLeakageError):
        redactor.assert_clean(f"Leaked secret: {test_secret}")

    # Should pass cleanly for sanitized text
    redactor.assert_clean("Safe and clean operational status output")
