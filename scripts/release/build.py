"""Deterministic, reproducible release build automation (T115).

Builds canonical distribution artifacts in `dist/`:
- Python Wheel: ai_software_co_agent-0.1.0-py3-none-any.whl
- Python Sdist: ai_software_co_agent-0.1.0.tar.gz
- Checksums: dist/SHA256SUMS.txt
- Manifest: dist/build_manifest.json

Ensures reproducibility:
- Alphabetically sorted file entries
- Normalized, deterministic timestamps (1980-01-01 00:00:00 UTC)
- Normalized line endings and file permissions
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import sys
import tarfile
import tomllib
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

FIXED_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_TIMESTAMP = 315532800  # 1980-01-01 00:00:00 UTC


def compute_sha256(data: bytes) -> str:
    """Compute hex SHA-256 digest of data bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of a file on disk."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _urlsafe_b64encode_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def load_project_metadata(root: Path) -> dict[str, Any]:
    """Load metadata from pyproject.toml."""
    pyproject_path = root / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
    return data.get("project", {})


def build_wheel(root: Path, dist_dir: Path, version: str) -> Path:
    """Build a deterministic, reproducible Python wheel."""
    pkg_name = "ai_software_co_agent"
    wheel_filename = f"{pkg_name}-{version}-py3-none-any.whl"
    wheel_path = dist_dir / wheel_filename

    dist_info = f"{pkg_name}-{version}.dist-info"

    metadata_content = (
        "Metadata-Version: 2.1\n"
        "Name: ai-software-co-agent\n"
        f"Version: {version}\n"
        "Summary: AI Software Co-Agent\n"
        "Author: AI Software Co-Agent Team\n"
        "License: MIT\n"
        "Requires-Python: >=3.14,<3.15\n"
        "Requires-Dist: pydantic>=2,<3\n"
        "\n"
        "# AI Software Co-Agent\n"
        "Deterministic, policy-guarded AI software engineering agent.\n"
    ).encode()

    wheel_meta = (
        b"Wheel-Version: 1.0\n"
        b"Generator: coagent-release-builder (0.1.0)\n"
        b"Root-Is-Purelib: true\n"
        b"Tag: py3-none-any\n"
    )

    entry_points = (
        b"[console_scripts]\n"
        b"coagent = coagent_cli.main:main\n"
    )

    record_entries: list[tuple[str, str, int]] = []

    # Collect source files
    src_files: list[tuple[str, Path]] = []
    
    # src/coagent -> coagent/
    coagent_dir = root / "src" / "coagent"
    for p in sorted(coagent_dir.rglob("*.py")):
        rel = p.relative_to(root / "src").as_posix()
        src_files.append((rel, p))

    # cli/coagent_cli -> coagent_cli/
    cli_dir = root / "cli" / "coagent_cli"
    for p in sorted(cli_dir.rglob("*.py")):
        rel = p.relative_to(root / "cli").as_posix()
        src_files.append((rel, p))

    src_files.sort(key=lambda x: x[0])

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for archive_name, disk_path in src_files:
            data = disk_path.read_bytes()
            # Normalize line endings to LF for reproducibility
            data = data.replace(b"\r\n", b"\n")
            zinfo = zipfile.ZipInfo(archive_name, date_time=FIXED_TIME)
            zinfo.external_attr = 0o644 << 16
            zf.writestr(zinfo, data)
            
            digest = _urlsafe_b64encode_nopad(hashlib.sha256(data).digest())
            record_entries.append((archive_name, f"sha256={digest}", len(data)))

        # Write dist-info metadata files
        for arcname, payload in [
            (f"{dist_info}/METADATA", metadata_content),
            (f"{dist_info}/WHEEL", wheel_meta),
            (f"{dist_info}/entry_points.txt", entry_points),
        ]:
            zinfo = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            zinfo.external_attr = 0o644 << 16
            zf.writestr(zinfo, payload)
            digest = _urlsafe_b64encode_nopad(hashlib.sha256(payload).digest())
            record_entries.append((arcname, f"sha256={digest}", len(payload)))

        # RECORD file itself
        record_lines = [f"{name},{hash_str},{size}" for name, hash_str, size in record_entries]
        record_lines.append(f"{dist_info}/RECORD,,")
        record_bytes = ("\n".join(record_lines) + "\n").encode("utf-8")
        
        zinfo = zipfile.ZipInfo(f"{dist_info}/RECORD", date_time=FIXED_TIME)
        zinfo.external_attr = 0o644 << 16
        zf.writestr(zinfo, record_bytes)

    return wheel_path


def build_sdist(root: Path, dist_dir: Path, version: str) -> Path:
    """Build a deterministic, reproducible source distribution (.tar.gz)."""
    pkg_name = f"ai_software_co_agent-{version}"
    sdist_filename = f"{pkg_name}.tar.gz"
    sdist_path = dist_dir / sdist_filename

    entries: list[tuple[str, Path]] = []

    # Root metadata files
    for fname in ["pyproject.toml", "README.md", "LICENSE"]:
        p = root / fname
        if p.exists():
            entries.append((f"{pkg_name}/{fname}", p))

    # Python packages
    coagent_dir = root / "src" / "coagent"
    for p in sorted(coagent_dir.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        entries.append((f"{pkg_name}/{rel}", p))

    cli_dir = root / "cli" / "coagent_cli"
    for p in sorted(cli_dir.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        entries.append((f"{pkg_name}/{rel}", p))

    entries.sort(key=lambda x: x[0])

    with sdist_path.open("wb") as f_out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f_out, mtime=FIXED_TIMESTAMP) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                # PKG-INFO
                pkg_info_content = (
                    "Metadata-Version: 2.1\n"
                    "Name: ai-software-co-agent\n"
                    f"Version: {version}\n"
                    "Summary: AI Software Co-Agent\n"
                    "Author: AI Software Co-Agent Team\n"
                    "License: MIT\n"
                    "Requires-Python: >=3.14,<3.15\n"
                    "Requires-Dist: pydantic>=2,<3\n"
                ).encode()

                ti_pkg = tarfile.TarInfo(name=f"{pkg_name}/PKG-INFO")
                ti_pkg.size = len(pkg_info_content)
                ti_pkg.mtime = FIXED_TIMESTAMP
                ti_pkg.mode = 0o644
                tar.addfile(ti_pkg, fileobj=io.BytesIO(pkg_info_content))

                for arcname, disk_path in entries:
                    data = disk_path.read_bytes().replace(b"\r\n", b"\n")
                    ti = tarfile.TarInfo(name=arcname)
                    ti.size = len(data)
                    ti.mtime = FIXED_TIMESTAMP
                    ti.mode = 0o644
                    tar.addfile(ti, fileobj=io.BytesIO(data))

    return sdist_path


def build_release(root: Path | None = None) -> dict[str, Any]:
    """Execute reproducible release build and write manifest and checksums."""
    project_root = root or Path(__file__).resolve().parent.parent.parent
    dist_dir = project_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    metadata = load_project_metadata(project_root)
    version = metadata.get("version", "0.1.0")

    print(f"Building release artifacts for ai-software-co-agent v{version}...")

    wheel_path = build_wheel(project_root, dist_dir, version)
    sdist_path = build_sdist(project_root, dist_dir, version)

    artifacts = [wheel_path, sdist_path]
    checksum_lines: list[str] = []
    manifest_artifacts: list[dict[str, Any]] = []

    for art in artifacts:
        sha = compute_file_sha256(art)
        size = art.stat().st_size
        checksum_lines.append(f"{sha}  {art.name}")
        manifest_artifacts.append({
            "name": art.name,
            "sha256": sha,
            "size_bytes": size,
            "type": "wheel" if art.name.endswith(".whl") else "sdist",
        })
        print(f"  Created: {art.name} ({size} bytes, sha256: {sha[:12]}...)")

    # Write SHA256SUMS.txt
    sums_path = dist_dir / "SHA256SUMS.txt"
    sums_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(f"  Generated: {sums_path.name}")

    # Write build_manifest.json
    manifest = {
        "project": "ai-software-co-agent",
        "version": version,
        "built_at": datetime.now(UTC).isoformat(),
        "python_requires": metadata.get("requires-python", ">=3.14,<3.15"),
        "artifacts": manifest_artifacts,
        "reproducible": True,
        "fixed_timestamp": FIXED_TIMESTAMP,
    }
    manifest_path = dist_dir / "build_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  Generated: {manifest_path.name}")

    return manifest


def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    build_release(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
