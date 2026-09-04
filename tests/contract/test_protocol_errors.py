from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.core.types import EventSeverity
from coagent.protocol.errors import (
    ProtocolError,
    ProtocolErrorCode,
    ProtocolErrorEnvelope,
)
from coagent.protocol.messages import PROTOCOL_VERSION

CANONICAL_MESSAGES = {
    ProtocolErrorCode.MALFORMED_MESSAGE: "Malformed protocol message.",
    ProtocolErrorCode.UNSUPPORTED_PROTOCOL_VERSION: "Unsupported protocol version.",
    ProtocolErrorCode.INVALID_REQUEST: "Invalid request.",
    ProtocolErrorCode.UNKNOWN_REQUEST_TYPE: "Unknown request type.",
    ProtocolErrorCode.MISSING_REQUIRED_FIELD: "Missing required field.",
    ProtocolErrorCode.INVALID_FIELD: "Invalid field.",
    ProtocolErrorCode.INVALID_FIELD_TYPE: "Invalid field type.",
    ProtocolErrorCode.INVALID_CORRELATION_ID: "Invalid correlation ID.",
    ProtocolErrorCode.PAYLOAD_INVALID: "Invalid payload.",
}


@pytest.mark.parametrize("code", list(ProtocolErrorCode))
def test_all_protocol_error_codes_have_stable_wire_values(
    code: ProtocolErrorCode,
) -> None:
    assert code.value == code.name


@pytest.mark.parametrize("code", list(ProtocolErrorCode))
def test_protocol_error_accepts_canonical_message(
    code: ProtocolErrorCode,
) -> None:
    error = ProtocolError(
        code=code,
        message=CANONICAL_MESSAGES[code],
    )

    assert error.code == code
    assert error.message == CANONICAL_MESSAGES[code]


@pytest.mark.parametrize("code", list(ProtocolErrorCode))
def test_protocol_error_rejects_noncanonical_message(
    code: ProtocolErrorCode,
) -> None:
    with pytest.raises(ValidationError):
        ProtocolError(
            code=code,
            message="Unsafe or arbitrary message.",
        )


def test_protocol_error_supports_request_id_and_details() -> None:
    request_id = uuid4()

    error = ProtocolError(
        code=ProtocolErrorCode.INVALID_REQUEST,
        message=CANONICAL_MESSAGES[ProtocolErrorCode.INVALID_REQUEST],
        request_id=request_id,
        details={
            "field": "payload",
            "reason": "invalid structure",
        },
    )

    assert error.request_id == request_id
    assert error.details == {
        "field": "payload",
        "reason": "invalid structure",
    }


def test_protocol_error_defaults_request_id_and_details() -> None:
    error = ProtocolError(
        code=ProtocolErrorCode.MALFORMED_MESSAGE,
        message=CANONICAL_MESSAGES[ProtocolErrorCode.MALFORMED_MESSAGE],
    )

    assert error.request_id is None
    assert error.details == {}


def test_protocol_error_rejects_invalid_request_id() -> None:
    with pytest.raises(ValidationError):
        ProtocolError(
            code=ProtocolErrorCode.INVALID_CORRELATION_ID,
            message=CANONICAL_MESSAGES[ProtocolErrorCode.INVALID_CORRELATION_ID],
            request_id="not-a-uuid",  # type: ignore[arg-type]
        )


def test_protocol_error_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProtocolError(
            code=ProtocolErrorCode.INVALID_REQUEST,
            message=CANONICAL_MESSAGES[ProtocolErrorCode.INVALID_REQUEST],
            unexpected="value",  # type: ignore[call-arg]
        )


def test_protocol_error_envelope_contains_required_fields() -> None:
    request_id = uuid4()
    created_at = datetime.now(UTC)

    envelope = ProtocolErrorEnvelope(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        error=ProtocolError(
            code=ProtocolErrorCode.INVALID_REQUEST,
            message=CANONICAL_MESSAGES[ProtocolErrorCode.INVALID_REQUEST],
            request_id=request_id,
        ),
        created_at=created_at,
    )

    assert envelope.protocol_version == PROTOCOL_VERSION
    assert envelope.request_id == request_id
    assert envelope.error.request_id == request_id
    assert envelope.created_at == created_at


def test_protocol_error_envelope_allows_null_request_id() -> None:
    envelope = ProtocolErrorEnvelope(
        protocol_version=PROTOCOL_VERSION,
        request_id=None,
        error=ProtocolError(
            code=ProtocolErrorCode.MALFORMED_MESSAGE,
            message=CANONICAL_MESSAGES[ProtocolErrorCode.MALFORMED_MESSAGE],
        ),
        created_at=datetime.now(UTC),
    )

    assert envelope.request_id is None
    assert envelope.error.request_id is None


def test_protocol_error_envelope_rejects_unsupported_version() -> None:
    with pytest.raises(ValidationError):
        ProtocolErrorEnvelope(
            protocol_version="999.0",
            request_id=None,
            error=ProtocolError(
                code=ProtocolErrorCode.MALFORMED_MESSAGE,
                message=CANONICAL_MESSAGES[ProtocolErrorCode.MALFORMED_MESSAGE],
            ),
            created_at=datetime.now(UTC),
        )


def test_protocol_error_envelope_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProtocolErrorEnvelope(
            protocol_version=PROTOCOL_VERSION,
            request_id=None,
            error=ProtocolError(
                code=ProtocolErrorCode.MALFORMED_MESSAGE,
                message=CANONICAL_MESSAGES[ProtocolErrorCode.MALFORMED_MESSAGE],
            ),
            created_at=datetime.now(UTC),
            unexpected="value",  # type: ignore[call-arg]
        )


def test_protocol_error_json_roundtrip() -> None:
    request_id = uuid4()
    created_at = datetime.now(UTC)

    envelope = ProtocolErrorEnvelope(
        protocol_version=PROTOCOL_VERSION,
        request_id=request_id,
        error=ProtocolError(
            code=ProtocolErrorCode.PAYLOAD_INVALID,
            message=CANONICAL_MESSAGES[ProtocolErrorCode.PAYLOAD_INVALID],
            request_id=request_id,
            details={
                "field": "payload",
                "reason": "invalid structure",
            },
        ),
        created_at=created_at,
    )

    serialized = envelope.model_dump_json()
    restored = ProtocolErrorEnvelope.model_validate_json(serialized)

    assert restored == envelope


def test_protocol_error_does_not_expose_sensitive_runtime_fields() -> None:
    fields = set(ProtocolError.model_fields)

    assert "affected_scope" not in fields
    assert "retry_key" not in fields
    assert "evidence_refs" not in fields


def test_protocol_error_envelope_uses_expected_severity_vocabulary_elsewhere() -> None:
    assert [severity.value for severity in EventSeverity] == [
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]
