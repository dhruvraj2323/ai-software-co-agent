"""Dependency and License Review CI script.

Verifies T113, ADM-035, and Release Gate compliance:
- Audits dependencies defined in pyproject.toml
- Verifies all production dependencies use approved permissive licenses
- Disallows viral copyleft (GPL, AGPL) or proprietary unapproved packages
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

# Allowlist of permitted open-source licenses for release builds
APPROVED_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "PSF-2.0",
    "Python-2.0",
    "ISC",
}

# Known dependency license mapping
PACKAGE_LICENSE_MAP = {
    "pydantic": "MIT",
    "pydantic-core": "MIT",
    "typing-extensions": "Python-2.0",
    "annotated-types": "MIT",
    "pytest": "MIT",
    "ruff": "MIT",
    "mypy": "MIT",
}


def audit_dependencies(pyproject_path: Path) -> tuple[bool, list[str]]:
    """Audit project dependencies against license and security policy."""
    if not pyproject_path.exists():
        return False, [f"pyproject.toml not found at {pyproject_path}"]

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    deps = project.get("dependencies", [])
    errors: list[str] = []

    for dep in deps:
        # Extract base package name (e.g. "pydantic>=2,<3" -> "pydantic")
        pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].split(">")[0].strip()
        license_name = PACKAGE_LICENSE_MAP.get(pkg_name.lower())

        if not license_name:
            errors.append(f"Unreviewed dependency '{pkg_name}' without license classification.")
        elif license_name not in APPROVED_LICENSES:
            errors.append(
                f"Dependency '{pkg_name}' has unapproved license '{license_name}'."
            )

    return len(errors) == 0, errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    pyproject = root / "pyproject.toml"
    success, errors = audit_dependencies(pyproject)

    if not success:
        print("DEPENDENCY / LICENSE AUDIT: FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("DEPENDENCY / LICENSE AUDIT: PASS")
    print(f"Audited {pyproject.name} successfully. All release dependencies approved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

