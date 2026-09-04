from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from coagent.protocol.messages import ProtocolMessage


class ProtocolErrorCode(StrEnum):
    MALFORMED_MESSAGE = "MALFORMED_MESSAGE"
    UNSUPPORTED_PROTOCOL_VERSION = "UNSUPPORTED_PROTOCOL_VERSION"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNKNOWN_REQUEST_TYPE = "UNKNOWN_REQUEST_TYPE"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD = "INVALID_FIELD"
    INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
    INVALID_CORRELATION_ID = "INVALID_CORRELATION_ID"
    PAYLOAD_INVALID = "PAYLOAD_INVALID"


_CANONICAL_MESSAGES: dict[ProtocolErrorCode, str] = {
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


class ProtocolError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ProtocolErrorCode
    message: str
    request_id: UUID | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str, info: Any) -> str:
        code = info.data.get("code")
        if code is not None and value != _CANONICAL_MESSAGES[code]:
            raise ValueError("message must match the canonical message for code")
        return value


class ProtocolErrorEnvelope(ProtocolMessage):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID | None = None
    error: ProtocolError
    created_at: datetime
