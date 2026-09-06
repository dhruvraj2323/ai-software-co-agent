"""Secret detection and redaction primitives."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

REDACTION_MARKER = "[REDACTED]"
@dataclass(frozen=True)
class SecretPattern:
    """Configured secret-detection pattern."""
    name: str
    pattern: str
    replacement: str = REDACTION_MARKER
    def compile(self) -> re.Pattern[str]:
        """Compile the configured secret pattern."""
        try:
            return re.compile(self.pattern, re.DOTALL)
        except re.error as exc:
            raise ValueError(
                f"invalid secret pattern '{self.name}': {exc}"
            ) from exc
class SecretRedactor:
    """Deterministically detect and redact sensitive values."""
    _BUILTIN_PATTERNS = (
        SecretPattern(
            name="private_key",
            pattern=(
                r"-----BEGIN "
                r"(?:RSA |EC |OPENSSH |DSA |ED25519 )?"
                r"PRIVATE KEY-----"
                r".*?"
                r"-----END "
                r"(?:RSA |EC |OPENSSH |DSA |ED25519 )?"
                r"PRIVATE KEY-----"
            ),
        ),
        SecretPattern(
            name="github_token",
            pattern=r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
        ),
        SecretPattern(
            name="aws_access_key",
            pattern=r"\bAKIA[0-9A-Z]{16}\b",
        ),
        SecretPattern(
            name="bearer_token",
            pattern=r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/=-]{8,}",
            replacement=r"\1" + REDACTION_MARKER,
        ),
        SecretPattern(
            name="token_assignment",
            pattern=(
                r"(?i)(\btoken\s*[:=]\s*['\"]?)[^'\"\s,;]+"
            ),
            replacement=r"\1" + REDACTION_MARKER,
        ),
        SecretPattern(
            name="api_key_assignment",
            pattern=(
                r"(?i)(\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|"
                r"auth[_-]?token)\s*[:=]\s*['\"]?)[^'\"\s,;]+"
            ),
            replacement=r"\1" + REDACTION_MARKER,
        ),
        SecretPattern(
            name="password_assignment",
            pattern=(
                r"(?i)(\b(?:password|passwd|pwd)\s*[:=]\s*['\"]?)[^'\"\s,;]+"
            ),
            replacement=r"\1" + REDACTION_MARKER,
        ),
        SecretPattern(
            name="secret_assignment",
            pattern=r"(?i)(\bsecret\s*[:=]\s*['\"]?)[^'\"\s,;]+",
            replacement=r"\1" + REDACTION_MARKER,
        ),
    )
    def __init__(
        self,
        patterns: tuple[SecretPattern, ...] = (),
    ) -> None:
        """Create a redactor with built-in and configured patterns."""
        self._patterns = tuple(
            (pattern, pattern.compile())
            for pattern in (*self._BUILTIN_PATTERNS, *patterns)
        )
    def redact(self, value: Any) -> Any:
        """Return a redacted copy of a value."""
        if isinstance(value, str):
            return self._redact_string(value)
        if isinstance(value, dict):
            return {
                key: self.redact(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self.redact(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self.redact(item) for item in value)
        if isinstance(value, set):
            return {self.redact(item) for item in value}
        return value
    def contains_secret(self, value: Any) -> bool:
        """Return whether a value contains a recognized secret pattern."""
        if isinstance(value, str):
            return any(
                compiled.search(value) is not None
                for _, compiled in self._patterns
            )
        if isinstance(value, dict):
            return any(
                self.contains_secret(key) or self.contains_secret(item)
                for key, item in value.items()
            )
        if isinstance(value, (list, tuple, set)):
            return any(self.contains_secret(item) for item in value)
        return False
    def _redact_string(self, value: str) -> str:
        """Redact all configured secret matches from a string."""
        redacted = value
        for pattern, compiled in self._patterns:
            redacted = compiled.sub(pattern.replacement, redacted)
        return redacted
def redact_secrets(
    value: Any,
    *,
    patterns: tuple[SecretPattern, ...] = (),
) -> Any:
    """Redact recognized secrets from a value."""
    return SecretRedactor(patterns).redact(value)
def contains_secret(
    value: Any,
    *,
    patterns: tuple[SecretPattern, ...] = (),
) -> bool:
    """Return whether a recognized secret exists in a value."""
    return SecretRedactor(patterns).contains_secret(value)
