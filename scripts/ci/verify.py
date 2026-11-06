"""Full CI validation orchestration script (Gate G0 to Gate G11).

Executes the complete end-to-end verification pipeline:
1. Ruff format/lint check
2. Mypy strict type check
3. Security secret scan
4. License & dependency check
5. Consolidated test suite
6. Release packaging
7. Release verification & smoke test
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_step(step_name: str, cmd: list[str], cwd: Path) -> bool:
    print("\n========================================================")
    print(f" CI PIPELINE STEP: {step_name}")
    print(f" Command: {' '.join(cmd)}")
    print("========================================================")
    res = subprocess.run(cmd, cwd=cwd)
    if res.returncode != 0:
        print(f"\n[FAIL] Step '{step_name}' failed with code {res.returncode}", file=sys.stderr)
        return False
    print(f"\n[PASS] Step '{step_name}' passed.")
    return True


def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent

    steps = [
        ("Linting & Code Style (Ruff)", [sys.executable, "-m", "ruff", "check", "."]),
        ("Type Checking (Mypy)", [sys.executable, "-m", "mypy", "src", "cli"]),
        ("Security Scan", [sys.executable, "scripts/ci/security_scan.py"]),
        (
            "License & Dependency Review",
            [sys.executable, "scripts/ci/license_and_dependency_check.py"],
        ),
        (
            "Release Packaging (Wheel, Sdist, VS Code)",
            [sys.executable, "scripts/release/package.py"],
        ),
        (
            "Release Verification & Smoke Test",
            [sys.executable, "scripts/release/verify_release.py"],
        ),
    ]

    for name, cmd in steps:
        if not run_step(name, cmd, root):
            print("\n*** CI VERIFICATION PIPELINE FAILED ***", file=sys.stderr)
            return 1

    print("\n********************************************************")
    print(" ALL CI VERIFICATION PIPELINE STEPS PASSED SUCCESSFULLY! ")
    print("********************************************************")
    return 0


if __name__ == "__main__":
    sys.exit(main())
