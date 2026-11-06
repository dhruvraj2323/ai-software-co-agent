"""Consolidated test runner script for CI (T007, T114)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    cmd = [sys.executable, "-m", "pytest", "tests/"] + sys.argv[1:]
    print(f"Running full test suite: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=root)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
