"""Dependency, License, and Security Review Test Suite.

Verifies T113, ADM-035, and Release Gate G10 security criteria:
- All production dependencies use approved permissive licenses
- No viral copyleft or unapproved licenses
- Dependency manifests are version-bounded and non-wildcard
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.ci.license_and_dependency_check import (
    APPROVED_LICENSES,
    audit_dependencies,
)


def test_pyproject_dependencies_licensed() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    pyproject_path = root / "pyproject.toml"

    success, errors = audit_dependencies(pyproject_path)
    assert success is True, f"Dependency audit failed: {errors}"


def test_dependencies_bounded_versions() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    pyproject_path = root / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    deps = data.get("project", {}) .get("dependencies", [])
    for dep in deps:
        # Every production dependency must have explicit version constraints (>= or ==)
        assert any(op in dep for op in (">=", "==", "~=")), f"Dependency {dep} lacks version bounds"


def test_approved_licenses_contain_no_copyleft() -> None:
    # Ensure allowlist only contains permissive open-source licenses
    forbidden_terms = ["GPL", "AGPL", "SSPL", "PROPRIETARY", "COMMERCIAL"]
    for lic in APPROVED_LICENSES:
        for term in forbidden_terms:
            assert term not in lic.upper()

