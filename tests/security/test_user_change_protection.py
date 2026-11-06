"""User Change Protection and Dirty Git State Security Test Suite.

Verifies ST-GIT-001, ADM-020, ADM-T09 according to:
- docs/specifications/10 AI_Software_CoAgent_Security_Sandbox_Specification_v1.0_FINAL_LOCKED.md
- docs/specifications/09 AI_Software_CoAgent_Testing_Validation_Specification_v1.0_FINAL_LOCKED.md
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from coagent.execution.filesystem import FilesystemExecutor
from coagent.execution.patch import (
    FilePatch,
    Patch,
    PatchConflictError,
    PatchEngine,
    PatchOperationType,
)
from coagent.git.adapter import GitAdapter
from coagent.policy.evaluator import (
    PolicyDecisionOutcome,
    PolicyEvaluator,
    PolicyRequest,
)
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequest,
    ToolRequestSource,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.workspace.scope import WorkspaceScope


def make_tool_def(
    tool_id: str,
    capability: ToolCapability,
    risk_level: ToolRiskLevel = ToolRiskLevel.HIGH,
    side_effects: list[ToolSideEffect] | None = None,
    resource_scope: ToolScope = ToolScope.WORKSPACE,
) -> ToolDefinition:
    return ToolDefinition(
        tool_id=tool_id,
        name=tool_id,
        description=f"Test capability for {tool_id}",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=capability,
        risk_level=risk_level,
        side_effects=side_effects or [ToolSideEffect.READ],
        resource_scope=resource_scope,
        approval_profile="default",
        executor="test",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "user_protected_repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test User"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )

    # Initial committed file
    (repo / "shared.py").write_text("def shared(): return 'base'\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "initial commit"],
        check=True,
        capture_output=True,
    )

    # Uncommitted user changes (dirty tree)
    (repo / "user_notes.txt").write_text("Critical user uncommitted thoughts\n", encoding="utf-8")
    (repo / "shared.py").write_text("def shared(): return 'user_modified'\n", encoding="utf-8")
    return repo


@pytest.fixture
def scope(git_repo: Path) -> WorkspaceScope:
    return WorkspaceScope(
        task_id=uuid4(),
        workspace_id=uuid4(),
        root=str(git_repo),
    )


# ST-GIT-001 (1): Unrelated user files remain completely safe during agent tasks
def test_unrelated_user_files_preserved(git_repo: Path, scope: WorkspaceScope) -> None:
    fs = FilesystemExecutor()
    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.write",
        tool_version="1.0",
        arguments={"path": "agent_feature.py", "content": "# Agent feature code\n"},
        requested_scope=Scope(workspace_id=uuid4(), root=str(git_repo)),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    tool_def = make_tool_def(
        "workspace.write",
        ToolCapability.WORKSPACE_WRITE,
        side_effects=[ToolSideEffect.WRITE],
    )
    res = fs.execute(req, tool_def)
    assert res.success

    # Verify user's uncommitted files and modifications are preserved untouched
    user_notes = (git_repo / "user_notes.txt").read_text(encoding="utf-8")
    assert user_notes == "Critical user uncommitted thoughts\n"
    shared_text = (git_repo / "shared.py").read_text(encoding="utf-8")
    assert shared_text == "def shared(): return 'user_modified'\n"


# ST-GIT-001 (2): Patch conflict detected when agent attempts to edit user-modified file
def test_patch_conflict_on_user_modified_file(git_repo: Path, scope: WorkspaceScope) -> None:
    engine = PatchEngine()
    shared_path = git_repo / "shared.py"

    patch = Patch(
        task_id=scope.task_id,
        expected_scope=["shared.py"],
        file_patches=[
            FilePatch(
                path="shared.py",
                operation=PatchOperationType.MODIFY,
                base_hash="stale_base_hash_1234567890abcdef",  # Hash mismatch with user's edits
                content="def shared(): return 'agent_overwritten'\n",
            )
        ],
    )

    # Validate fails with PatchConflictError because user modified the file
    with pytest.raises(PatchConflictError):
        engine.validate(patch, scope)

    # User's modification is intact
    assert shared_path.read_text(encoding="utf-8") == "def shared(): return 'user_modified'\n"


# ST-GIT-001 (3): Destructive Git operations are rejected by policy
def test_destructive_git_policy_rejection() -> None:
    evaluator = PolicyEvaluator()
    git_tool_def = make_tool_def(
        tool_id="git.rollback",
        capability=ToolCapability.GIT_ROLLBACK,
        risk_level=ToolRiskLevel.HIGH,
        side_effects=[ToolSideEffect.DESTRUCTIVE],
        resource_scope=ToolScope.WORKSPACE,
    )

    req = PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="git.rollback",
        tool_version="1.0",
        arguments={"hard": True, "clean_untracked": True},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/workspace"),
        autonomy_mode=AutonomyMode.RESTRICTED,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.HIGH,
        created_at=datetime.now(UTC),
    )
    decision = evaluator.evaluate(req, git_tool_def)
    # High-risk destructive git operation cannot execute in restricted mode
    assert decision.outcome != PolicyDecisionOutcome.ALLOW


# ST-GIT-001 (4): GitAdapter detects dirty working tree and uncommitted user edits
def test_git_adapter_dirty_tree_detection(git_repo: Path) -> None:
    adapter = GitAdapter(git_repo)
    status = adapter.get_status()

    # Git status correctly reports uncommitted modifications and untracked user files
    assert not status.is_clean
    assert any("shared.py" in str(f) for f in status.modified_files)
    assert any("user_notes.txt" in str(f) for f in status.untracked_files)
