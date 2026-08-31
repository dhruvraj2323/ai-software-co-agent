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

    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern, description in SECRET_PATTERNS:
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

    print("SECURITY SCAN: PASS")
    print(f"Scanned {len(iter_files())} files.")
    print("No configured secret patterns were detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
