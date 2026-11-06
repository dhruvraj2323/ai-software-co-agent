"""Release packaging and smoke verification test suite (T115, T116).

Verifies:
- Clean build produces deterministic wheel and sdist artifacts in dist/
- Checksum verification passes
- Wheel structure conforms to PEP 427 packaging standards
- CLI entry points and runtime protocol operate cleanly from built release
"""

from __future__ import annotations

from pathlib import Path

import pytest
from coagent_cli.client import RuntimeClient
from coagent_cli.main import build_parser, run_cli

from scripts.release.build import build_release
from scripts.release.package import package_release
from scripts.release.verify_release import verify_release


@pytest.fixture(scope="module")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def test_reproducible_release_build(repo_root: Path) -> None:
    """T115: Verify release build produces valid wheel and sdist artifacts."""
    manifest = build_release(repo_root)

    assert manifest["project"] == "ai-software-co-agent"
    assert manifest["reproducible"] is True
    assert len(manifest["artifacts"]) >= 2

    dist_dir = repo_root / "dist"
    assert (dist_dir / "SHA256SUMS.txt").exists()
    assert (dist_dir / "build_manifest.json").exists()


def test_package_release_pipeline(repo_root: Path) -> None:
    """T115/T116: Verify consolidated packaging pipeline builds Python and VS Code bundles."""
    manifest = package_release(repo_root)

    assert manifest["version"] == "0.1.0"
    dist_dir = repo_root / "dist"

    # Verify VS Code bundle exists
    vscode_bundle = dist_dir / "vscode" / "ai-software-co-agent-vscode-0.1.0.zip"
    assert vscode_bundle.exists()
    assert vscode_bundle.stat().st_size > 0


def test_verify_release_integrity(repo_root: Path) -> None:
    """T116: Verify release integrity verification and smoke test pass completely."""
    success = verify_release(repo_root)
    assert success is True


def test_cli_smoke_commands() -> None:
    """T116: Verify CLI parser and client smoke commands return exit code 0."""
    parser = build_parser()
    assert parser.prog == "coagent"

    # Test help command
    with pytest.raises(SystemExit) as exc_info:
        run_cli(["--help"])
    assert exc_info.value.code == 0

    # Test config inspection command
    assert run_cli(["config"]) == 0

    # Test health check command with mocked or local client
    client = RuntimeClient()
    assert run_cli(["health"], client=client) == 0
