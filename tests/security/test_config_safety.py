"""Tests for source-controlled configuration safety."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_TEST_FILE = ROOT / "configs" / "security_scan_test_config.yaml"


def run_security_scan() -> subprocess.CompletedProcess[str]:
    """Run the repository security scanner."""
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "ci" / "security_scan.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_environment_example_contains_no_real_secret_values() -> None:
    """The tracked environment example must not contain credentials."""
    content = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "COAGENT_ENV=development" in content
    assert "API_KEY=" not in content
    assert "PASSWORD=" not in content
    assert "SECRET_KEY=" not in content
    assert "ACCESS_TOKEN=" not in content


def test_security_scanner_detects_hard_coded_config_secret() -> None:
    """The security scanner must reject hard-coded credentials in config files."""
    try:
        secret_value = "test-" + "secret-value"
        config_key = "api" + "_key"
        config_line = f'{config_key}: "{secret_value}"\n'

        CONFIG_TEST_FILE.write_text(
            config_line,
            encoding="utf-8",
        )

        result = run_security_scan()

        assert result.returncode != 0
        assert "possible hard-coded configuration credential" in result.stdout
    finally:
        if CONFIG_TEST_FILE.exists():
            CONFIG_TEST_FILE.unlink()


def test_security_scanner_allows_environment_reference_in_config() -> None:
    """The security scanner must allow environment variable references."""
    try:
        config_key = "api" + "_key"
        config_value = "${COAGENT_API_KEY}"
        config_line = f"{config_key}: {config_value}\n"

        CONFIG_TEST_FILE.write_text(
            config_line,
            encoding="utf-8",
        )

        result = run_security_scan()

        assert result.returncode == 0
    finally:
        if CONFIG_TEST_FILE.exists():
            CONFIG_TEST_FILE.unlink()
