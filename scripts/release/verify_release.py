"""Comprehensive release verification and smoke test runner (T116, Gate G11).

Validates:
1. Release artifact integrity in `dist/`
2. SHA-256 checksum verification against `dist/SHA256SUMS.txt`
3. Wheel standards compliance (dist-info, RECORD, entry_points.txt)
4. Isolated clean-room extraction and importability
5. CLI smoke test (`--help`, `config`, `health`)
6. End-to-end runtime daemon and client protocol verification
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release.build import compute_file_sha256, load_project_metadata  # noqa: E402


class ReleaseVerificationError(Exception):
    """Raised when release verification fails."""


def verify_checksums(dist_dir: Path) -> list[str]:
    """Verify all checksums in dist/SHA256SUMS.txt against on-disk files."""
    sums_file = dist_dir / "SHA256SUMS.txt"
    if not sums_file.exists():
        raise ReleaseVerificationError(f"Missing checksum file: {sums_file}")

    verified: list[str] = []
    lines = sums_file.read_text(encoding="utf-8").strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ReleaseVerificationError(f"Malformed checksum line: {line}")
        expected_sha, rel_path = parts
        file_path = dist_dir / rel_path
        if not file_path.exists():
            raise ReleaseVerificationError(
                f"File listed in SHA256SUMS.txt does not exist: {rel_path}"
            )
        actual_sha = compute_file_sha256(file_path)
        if actual_sha != expected_sha:
            raise ReleaseVerificationError(
                f"Checksum mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}"
            )
        verified.append(rel_path)

    return verified


def verify_wheel_structure(wheel_path: Path, version: str) -> None:
    """Verify standards compliance of the built wheel archive."""
    dist_info = f"ai_software_co_agent-{version}.dist-info"
    required_dist_info = [
        f"{dist_info}/METADATA",
        f"{dist_info}/WHEEL",
        f"{dist_info}/RECORD",
        f"{dist_info}/entry_points.txt",
    ]

    with zipfile.ZipFile(wheel_path, "r") as zf:
        names = set(zf.namelist())
        for req in required_dist_info:
            if req not in names:
                raise ReleaseVerificationError(f"Wheel missing required file: {req}")

        # Check console script entry point
        entry_points = zf.read(f"{dist_info}/entry_points.txt").decode("utf-8")
        if "coagent = coagent_cli.main:main" not in entry_points:
            raise ReleaseVerificationError(
                f"entry_points.txt missing 'coagent' console script:\n{entry_points}"
            )

        # Verify RECORD hashes
        record_content = zf.read(f"{dist_info}/RECORD").decode("utf-8")
        for line in record_content.strip().splitlines():
            row = line.split(",")
            fname = row[0]
            if fname.endswith("RECORD"):
                continue
            if len(row) < 3 or not row[1].startswith("sha256="):
                raise ReleaseVerificationError(f"Invalid RECORD line: {line}")
            expected_b64 = row[1].removeprefix("sha256=")
            data = zf.read(fname)
            digest = hashlib.sha256(data).digest()
            actual_b64 = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
            if actual_b64 != expected_b64:
                raise ReleaseVerificationError(f"RECORD hash mismatch for {fname}")


def run_smoke_test(wheel_path: Path) -> None:
    """Extract wheel into an isolated directory and run smoke tests."""
    with tempfile.TemporaryDirectory(prefix="coagent_smoke_") as tmpdir:
        extract_dir = Path(tmpdir)
        with zipfile.ZipFile(wheel_path, "r") as zf:
            zf.extractall(extract_dir)

        # Prepend extracted path to sys.path
        orig_sys_path = list(sys.path)
        sys.path.insert(0, str(extract_dir))

        try:
            # Test imports from extracted wheel
            import coagent_cli.client
            import coagent_cli.main


            # Test CLI parser help
            parser = coagent_cli.main.build_parser()
            assert parser.prog == "coagent"

            # Test CLI subcommands
            try:
                coagent_cli.main.run_cli(["--help"])
            except SystemExit as exc:
                if exc.code != 0:
                    raise ReleaseVerificationError(
                        f"CLI --help failed with exit code {exc.code}"
                    ) from exc

            exit_code = coagent_cli.main.run_cli(["config"])
            if exit_code != 0:
                raise ReleaseVerificationError(f"CLI config failed with exit code {exit_code}")

            # Test runtime client & service startup smoke test
            client = coagent_cli.client.RuntimeClient()
            health = client._service.health()
            if health.get("status") != "healthy":
                raise ReleaseVerificationError(f"Runtime service unhealthy: {health}")

            # Test task creation and status retrieval through protocol
            task_evt = client.create_task("Smoke test goal")
            task_id = task_evt.task_id
            status_evt = client.get_status(task_id=task_id)
            if status_evt.task_id != task_id:
                raise ReleaseVerificationError(f"Protocol task status mismatch: {status_evt}")

        finally:
            sys.path = orig_sys_path


def verify_release(root: Path | None = None) -> bool:
    """Run all verification steps for the current release."""
    project_root = root or Path(__file__).resolve().parent.parent.parent
    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        print(
            f"ERROR: dist directory not found at {dist_dir}. Run build or package first.",
            file=sys.stderr,
        )
        return False

    metadata = load_project_metadata(project_root)
    version = metadata.get("version", "0.1.0")

    print(f"=== Verifying Release for ai-software-co-agent v{version} ===")

    # 1. Verify Checksums
    print("[1/4] Verifying SHA256 checksums...")
    verified_files = verify_checksums(dist_dir)
    for vf in verified_files:
        print(f"  OK: {vf}")

    # 2. Verify Wheel
    print("[2/4] Verifying Wheel packaging standards...")
    wheel_name = f"ai_software_co_agent-{version}-py3-none-any.whl"
    wheel_path = dist_dir / wheel_name
    if not wheel_path.exists():
        raise ReleaseVerificationError(f"Missing wheel artifact: {wheel_path}")
    verify_wheel_structure(wheel_path, version)
    print(f"  OK: {wheel_name} conforms to wheel specifications")

    # 3. Verify Manifest
    print("[3/4] Verifying build manifest...")
    manifest_file = dist_dir / "build_manifest.json"
    if not manifest_file.exists():
        raise ReleaseVerificationError("Missing build_manifest.json")
    with manifest_file.open("r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    if manifest_data.get("version") != version:
        raise ReleaseVerificationError(
            f"Manifest version mismatch: {manifest_data.get('version')} vs {version}"
        )
    print(f"  OK: build_manifest.json matches v{version}")

    # 4. Isolated Smoke Test
    print("[4/4] Executing isolated smoke tests...")
    run_smoke_test(wheel_path)
    print("  OK: Clean import, CLI parser, runtime daemon, and protocol smoke tests passed")

    print("=== Release Verification PASSED Successfully ===")
    return True


def main() -> int:
    try:
        success = verify_release()
        return 0 if success else 1
    except Exception as exc:
        print(f"RELEASE VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
