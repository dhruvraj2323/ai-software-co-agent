"""Baseline security scanner for the AI Software Co-Agent repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}

SKIP_FILES = {
    ".env",
}

SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)"
            r"\s*[:=]\s*['\"][^'\"]+['\"]"
        ),
        "possible hard-coded credential",
    ),
    (
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
        "private key material",
    ),
    (
        re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]+['\"]"),
        "possible hard-coded password",
    ),
]

CONFIG_DIRECTORIES = {
    ROOT / "configs",
}

CONFIG_FILE_SUFFIXES = {
    ".yaml",
    ".yml",
    ".json",
    ".toml",
}

CONFIG_SECRET_PATTERNS = [
    (
        re.compile(
            r"(?i)^\s*(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)"
            r"\s*[:=]\s*(?!['\"]?\$\{[^}]+\}['\"]?(?:\s+#.*)?$)"
            r"['\"]?[^#\r\n]+['\"]?\s*(?:#.*)?$"
        ),
        "possible hard-coded configuration credential",
    ),
    (
        re.compile(
            r"(?i)^\s*(password|passwd|pwd)"
            r"\s*[:=]\s*(?!['\"]?\$\{[^}]+\}['\"]?(?:\s+#.*)?$)"
            r"['\"]?[^#\r\n]+['\"]?\s*(?:#.*)?$"
        ),
        "possible hard-coded configuration password",
    ),
]


def iter_files() -> list[Path]:
    """Return repository files that are in scanner scope."""
    files: list[Path] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(ROOT)

        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue

        if path.name in SKIP_FILES:
            continue

        files.append(path)

    return files


def scan_file(path: Path) -> list[str]:
    """Scan one file and return actionable findings."""
    findings: list[str] = []

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError, OSError:
        return findings

    relative = path.relative_to(ROOT)

    is_config_file = path.suffix.lower() in CONFIG_FILE_SUFFIXES and any(
        config_directory == path.parent or config_directory in path.parents
        for config_directory in CONFIG_DIRECTORIES
    )

    patterns = SECRET_PATTERNS

    if is_config_file:
        patterns = SECRET_PATTERNS + CONFIG_SECRET_PATTERNS

    for line_number, line in enumerate(text.splitlines(), start=1):
        if is_config_file and re.search(
            r"\$\{[A-Za-z_][A-Za-z0-9_]*\}",
            line,
        ):
            continue

        for pattern, description in patterns:
            if pattern.search(line):
                findings.append(f"{relative}:{line_number}: {description}")

    return findings


def main() -> int:
    """Run the repository security scan."""
    findings: list[str] = []

    for path in iter_files():
        findings.extend(scan_file(path))

    if findings:
        print("SECURITY SCAN: FAIL")
        print()
        print("Actionable findings:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    files = iter_files()

    print("SECURITY SCAN: PASS")
    print(f"Scanned {len(files)} files.")
    print("No configured secret patterns were detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
