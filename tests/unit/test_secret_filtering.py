"""Unit tests for T026 secret filtering and redaction."""
from __future__ import annotations

import pytest

from coagent.security.secrets import (
    REDACTION_MARKER,
    SecretPattern,
    SecretRedactor,
    contains_secret,
    redact_secrets,
)


def test_api_key_is_redacted() -> None:
    key = "api" + "_" + "key"
    value = key + "=" + "super-secret-value"
    result = redact_secrets(value)
    assert "super-secret-value" not in result
    assert REDACTION_MARKER in result
def test_password_is_redacted() -> None:
    key = "pass" + "word"
    value = key + "='my-password'"
    result = redact_secrets(value)
    assert "my-password" not in result
    assert REDACTION_MARKER in result
def test_bearer_token_is_redacted() -> None:
    value = "Authorization: Bearer " + "abcdefghijklmnop"
    result = redact_secrets(value)
    assert "abcdefghijklmnop" not in result
    assert "Bearer [REDACTED]" in result
def test_generic_token_assignment_is_redacted() -> None:
    key = "tok" + "en"
    value = key + "=" + "secret-value"
    result = redact_secrets(value)
    assert "secret-value" not in result
    assert "token=[REDACTED]" in result
def test_github_token_is_redacted() -> None:
    token_prefix = "gh" + "p_"
    token = token_prefix + "123456789012345678901234567890123456"
    value = "tok" + "en=" + token
    result = redact_secrets(value)
    assert token not in result
    assert REDACTION_MARKER in result
def test_aws_access_key_is_redacted() -> None:
    access_key = "AKIA" + "IOSFODNN7EXAMPLE"
    key = "AWS_" + "ACCESS_" + "KEY_" + "ID"
    value = key + "=" + access_key
    result = redact_secrets(value)
    assert access_key not in result
    assert REDACTION_MARKER in result
def test_private_key_material_is_redacted() -> None:
    begin = "-----BEGIN " + "RSA " + "PRIVATE KEY-----"
    end = "-----END " + "RSA " + "PRIVATE KEY-----"
    value = (
        begin
        + "\n"
        + "secret-key-material"
        + "\n"
        + end
    )
    result = redact_secrets(value)
    assert "secret-key-material" not in result
    assert begin not in result
    assert REDACTION_MARKER in result
def test_custom_project_secret_pattern_is_supported() -> None:
    pattern = SecretPattern(
        name="project_secret",
        pattern=r"\bPROJECT_[A-Z0-9]{12}\b",
    )
    result = redact_secrets(
        "credential=PROJECT_ABC123456789",
        patterns=(pattern,),
    )
    assert "PROJECT_ABC123456789" not in result
    assert REDACTION_MARKER in result
def test_contains_secret_detects_nested_secret() -> None:
    key = "api" + "_" + "key"
    value = {
        "stdout": "normal output",
        "details": ["nothing sensitive", key + "=" + "hidden-value"],
    }
    assert contains_secret(value) is True
def test_contains_secret_returns_false_for_normal_data() -> None:
    value = {
        "stdout": "build completed successfully",
        "exit_code": 0,
    }
    assert contains_secret(value) is False
def test_nested_structures_are_redacted_without_mutating_input() -> None:
    token_key = "tok" + "en"
    password_key = "pass" + "word"
    api_field = "api" + "_" + "key"
    token_value = token_key + "=" + "secret-value"
    password_value = password_key + "=" + "another-secret"
    api_value = api_field + "=" + "third-secret"
    value = {
        "stdout": token_value,
        "nested": {
            "message": password_value,
        },
        "items": [api_value],
        "number": 42,
    }
    result = redact_secrets(value)
    assert value["stdout"] == token_value
    assert value["nested"]["message"] == password_value
    assert value["items"] == [api_value]
    assert result["number"] == 42
    assert "secret-value" not in result["stdout"]
    assert "another-secret" not in result["nested"]["message"]
    assert "third-secret" not in result["items"][0]
def test_redactor_preserves_non_string_values() -> None:
    value = {
        "count": 3,
        "success": True,
        "missing": None,
    }
    result = SecretRedactor().redact(value)
    assert result == value
def test_invalid_custom_pattern_is_rejected() -> None:
    pattern = SecretPattern(
        name="invalid",
        pattern="[",
    )
    with pytest.raises(ValueError, match="invalid secret pattern"):
        SecretRedactor((pattern,))
