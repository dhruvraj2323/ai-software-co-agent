"""Consolidated release packaging automation (T115, T116).

Coordinates packaging of Python distributions, CLI binaries, VS Code extension bundle,
and release checksums into `dist/`.
"""

from __future__ import annotations

import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release.build import (  # noqa: E402
    FIXED_TIME,
    build_release,
    compute_file_sha256,
    load_project_metadata,
)


def package_vscode_extension(root: Path, dist_dir: Path, version: str) -> Path:
    """Package VS Code extension source bundle deterministically into dist/vscode/."""
    vscode_dist = dist_dir / "vscode"
    vscode_dist.mkdir(parents=True, exist_ok=True)
    ext_zip_path = vscode_dist / f"ai-software-co-agent-vscode-{version}.zip"

    src_dir = root / "vscode-extension"
    if not src_dir.exists():
        raise FileNotFoundError(f"VS Code extension directory not found: {src_dir}")

    files: list[tuple[str, Path]] = []
    for p in sorted(src_dir.rglob("*")):
        if p.is_file():
            rel = p.relative_to(src_dir).as_posix()
            # Exclude node_modules, temp, build artifacts
            if any(part in rel for part in ["node_modules", ".git", "out", "dist"]):
                continue
            files.append((f"vscode-extension/{rel}", p))

    files.sort(key=lambda x: x[0])

    with zipfile.ZipFile(ext_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for archive_name, disk_path in files:
            data = disk_path.read_bytes().replace(b"\r\n", b"\n")
            zinfo = zipfile.ZipInfo(archive_name, date_time=FIXED_TIME)
            zinfo.external_attr = 0o644 << 16
            zf.writestr(zinfo, data)

    return ext_zip_path


def package_release(root: Path | None = None) -> dict[str, Any]:
    """Execute complete release packaging pipeline."""
    project_root = root or Path(__file__).resolve().parent.parent.parent
    dist_dir = project_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    metadata = load_project_metadata(project_root)
    version = metadata.get("version", "0.1.0")

    print(f"=== Starting Release Packaging for ai-software-co-agent v{version} ===")

    # 1. Build Python artifacts (Wheel and Sdist)
    build_release(project_root)

    # 2. Package VS Code Extension
    print("Packaging VS Code Extension bundle...")
    ext_path = package_vscode_extension(project_root, dist_dir, version)
    rel_ext = ext_path.relative_to(project_root).as_posix()
    print(f"  Created: {rel_ext} ({ext_path.stat().st_size} bytes)")

    # 3. Aggregate all artifacts in dist/
    all_artifacts: list[Path] = []
    for p in sorted(dist_dir.rglob("*")):
        if (
            p.is_file()
            and not p.name.startswith(".")
            and p.name not in {"SHA256SUMS.txt", "build_manifest.json"}
        ):
            all_artifacts.append(p)

    checksum_lines: list[str] = []
    artifact_records: list[dict[str, Any]] = []

    for art in all_artifacts:
        sha = compute_file_sha256(art)
        rel_path = art.relative_to(dist_dir).as_posix()
        checksum_lines.append(f"{sha}  {rel_path}")
        artifact_records.append({
            "path": rel_path,
            "filename": art.name,
            "sha256": sha,
            "size_bytes": art.stat().st_size,
        })

    # Update SHA256SUMS.txt
    sums_path = dist_dir / "SHA256SUMS.txt"
    sums_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(f"  Updated: {sums_path.name}")

    # Update build_manifest.json
    final_manifest = {
        "project": "ai-software-co-agent",
        "version": version,
        "packaged_at": datetime.now(UTC).isoformat(),
        "python_requires": metadata.get("requires-python", ">=3.14,<3.15"),
        "artifacts": artifact_records,
        "reproducible": True,
    }
    manifest_path = dist_dir / "build_manifest.json"
    manifest_path.write_text(json.dumps(final_manifest, indent=2), encoding="utf-8")
    print(f"  Updated: {manifest_path.name}")

    print("=== Release Packaging Completed Successfully ===")
    return final_manifest


def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    package_release(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
