"""Unit tests for patch and conflict engine (T043, T044)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from coagent.execution.patch import (
    FilePatch,
    Patch,
    PatchEngine,
    PatchOperationType,
    compute_file_hash,
)
from coagent.workspace import WorkspaceScope


def make_scope(root: Path) -> WorkspaceScope:
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(root),
    )


def test_atomic_patch_create_and_modify(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    scope = make_scope(workspace)
    engine = PatchEngine()

    # 1. Create file via patch
    patch_create = Patch(
        task_id=uuid4(),
        expected_scope=["src/hello.py"],
        file_patches=[
            FilePatch(
                path="src/hello.py",
                operation=PatchOperationType.CREATE,
                content="def hello(): return 'world'\n",
            )
        ],
    )
    res_create = engine.apply(patch_create, scope)
    assert res_create.success is True
    assert (workspace / "src/hello.py").exists()

    # 2. Modify file with matching base hash
    file_path = workspace / "src/hello.py"
    current_hash = compute_file_hash(file_path)

    patch_mod = Patch(
        task_id=uuid4(),
        expected_scope=["src/hello.py"],
        file_patches=[
            FilePatch(
                path="src/hello.py",
                operation=PatchOperationType.MODIFY,
                base_hash=current_hash,
                content="def hello(): return 'co-agent'\n",
            )
        ],
    )
    res_mod = engine.apply(patch_mod, scope)
    assert res_mod.success is True
    assert "co-agent" in file_path.read_text(encoding="utf-8")
    assert "+def hello(): return 'co-agent'" in res_mod.diff


def test_patch_stale_hash_conflict_fails_closed(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "config.txt"
    target.write_text("initial version", encoding="utf-8")
    scope = make_scope(workspace)
    engine = PatchEngine()

    # Attempt to apply patch with stale hash
    stale_hash = "0" * 64
    patch = Patch(
        task_id=uuid4(),
        expected_scope=["config.txt"],
        file_patches=[
            FilePatch(
                path="config.txt",
                operation=PatchOperationType.MODIFY,
                base_hash=stale_hash,
                content="new version",
            )
        ],
    )
    res = engine.apply(patch, scope)
    assert res.success is False
    assert res.error_code == "PATCH_STALE_HASH"
    assert target.read_text(encoding="utf-8") == "initial version"  # Unchanged!


def test_patch_dry_run_leaves_disk_untouched(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    scope = make_scope(workspace)
    engine = PatchEngine()

    patch = Patch(
        task_id=uuid4(),
        expected_scope=["new_file.txt"],
        file_patches=[
            FilePatch(
                path="new_file.txt",
                operation=PatchOperationType.CREATE,
                content="temporary",
            )
        ],
        dry_run=True,
    )
    res = engine.apply(patch, scope)
    assert res.success is True
    assert res.dry_run is True
    assert not (workspace / "new_file.txt").exists()


def test_patch_out_of_scope_is_rejected(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    scope = make_scope(workspace)
    engine = PatchEngine()

    patch = Patch(
        task_id=uuid4(),
        expected_scope=["src/main.py"],
        file_patches=[
            FilePatch(
                path="unauthorized.py",
                operation=PatchOperationType.CREATE,
                content="attack",
            )
        ],
    )
    res = engine.apply(patch, scope)
    assert res.success is False
    assert res.error_code == "PATCH_OUT_OF_SCOPE"
    assert not (workspace / "unauthorized.py").exists()
