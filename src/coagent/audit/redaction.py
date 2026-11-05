"""Output redaction layer for audit events, artifacts, and traces (T090, TD-024)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from coagent.core.events import EventEnvelope
from coagent.security.secrets import SecretPattern, SecretRedactor


class SecretLeakageError(RuntimeError):
    """Raised when an unredacted secret is detected in sanitized audit output."""


class OutputRedactor:
    """Recursively redacts sensitive patterns, tokens, and credentials from audit structures."""

    def __init__(
        self,
        custom_patterns: tuple[SecretPattern, ...] = (),
        extra_secrets: set[str] | None = None,
    ) -> None:
        self._redactor = SecretRedactor(custom_patterns)
        self._extra_secrets: set[str] = {s for s in (extra_secrets or set()) if len(s.strip()) >= 4}

    def add_secret(self, secret: str) -> None:
        """Register a specific dynamic secret string to be redacted."""
        clean = secret.strip()
        if len(clean) >= 4:
            self._extra_secrets.add(clean)

    def redact_text(self, text: str) -> str:
        """Redact secrets from a string."""
        if not text:
            return text

        result = self._redactor.redact(text)
        for secret in self._extra_secrets:
            if secret in result:
                result = result.replace(secret, "[REDACTED]")
        return str(result)

    def redact_value(self, value: Any) -> Any:
        """Recursively redact strings in dicts, lists, tuples, sets, and Pydantic models."""
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, (int, float, bool, type(None), UUID)):
            return value
        if isinstance(value, dict):
            clean_dict: dict[str, Any] = {}
            for k, v in value.items():
                k_lower = str(k).lower()
                is_sensitive_key = any(
                    sens in k_lower
                    for sens in ("password", "passwd", "secret", "token", "api_key", "apikey")
                )
                if is_sensitive_key and isinstance(v, str):
                    clean_dict[k] = "[REDACTED]"
                else:
                    clean_dict[k] = self.redact_value(v)
            return clean_dict
        if isinstance(value, list):
            return [self.redact_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self.redact_value(item) for item in value)
        if isinstance(value, set):
            return {self.redact_value(item) for item in value}
        if isinstance(value, BaseModel):
            dumped = value.model_dump()
            return self.redact_value(dumped)
        return value

    def redact_event(self, event: EventEnvelope) -> EventEnvelope:
        """Return a scrubbed copy of an EventEnvelope with all secrets redacted."""
        clean_payload = self.redact_value(event.payload)
        clean_source = self.redact_text(event.source)

        return EventEnvelope(
            event_id=event.event_id,
            request_id=event.request_id,
            session_id=event.session_id,
            task_id=event.task_id,
            type=event.type,
            severity=event.severity,
            timestamp=event.timestamp,
            source=clean_source,
            payload=clean_payload,
            correlation_id=event.correlation_id,
        )

    def contains_secret(self, value: Any) -> bool:
        """Check whether value contains any configured or dynamic secret pattern."""
        if self._redactor.contains_secret(value):
            return True

        # Check extra registered secrets
        if isinstance(value, str):
            return any(s in value for s in self._extra_secrets)
        if isinstance(value, dict):
            sensitive_markers = ("password", "passwd", "secret", "token", "api_key", "apikey")
            for k, v in value.items():
                k_lower = str(k).lower()
                if any(sens in k_lower for sens in sensitive_markers):
                    if v != "[REDACTED]":
                        return True
                if self.contains_secret(k) or self.contains_secret(v):
                    return True
            return False
        if isinstance(value, (list, tuple, set)):
            return any(self.contains_secret(item) for item in value)
        if isinstance(value, BaseModel):
            return self.contains_secret(value.model_dump())
        return False

    def assert_clean(self, value: Any, context: str = "audit output") -> None:
        """Raise SecretLeakageError if the value contains any unredacted sensitive token."""
        if self.contains_secret(value):
            raise SecretLeakageError(f"Potential secret leakage detected in {context}.")
