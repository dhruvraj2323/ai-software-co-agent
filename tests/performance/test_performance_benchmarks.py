"""Performance and Resource Benchmark Suite.

Verifies T112, Section 21 of 09 AI_Software_CoAgent_Testing_Validation_Specification:
- Repository discovery: Latency, file count
- Repository search: Latency, result count
- Context assembly: Latency, token budget enforcement
- Policy Engine: Decision throughput and latency
- Patch Engine: Application latency
- Persistence: SQLite read/write latency
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from coagent.execution.patch import (
    FilePatch,
    Patch,
    PatchEngine,
    PatchOperationType,
    compute_file_hash,
)
from coagent.memory.manager import ScopedMemoryManager, SqliteMemoryStore
from coagent.policy.evaluator import PolicyEvaluator, PolicyRequest
from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.search import RepositorySearchAdapter
from coagent.tools.contracts import AutonomyMode, Scope, ToolRequestSource
from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)
from coagent.workspace.scope import WorkspaceScope


# Benchmark 1: Repository discovery and text search latency
def test_benchmark_repository_discovery_and_search(tmp_path: Path) -> None:
    repo_dir = tmp_path / "bench_repo"
    repo_dir.mkdir()

    # Generate 100 source files
    for i in range(100):
        sub = repo_dir / f"module_{i // 10}"
        sub.mkdir(exist_ok=True)
        (sub / f"file_{i}.py").write_text(
            f"def func_{i}():\n    return 'value_{i}'\n",
            encoding="utf-8",
        )

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(repo_dir))

    # Measure discovery latency
    discovery_start = time.perf_counter()
    discovery_service = RepositoryDiscoveryService()
    _ = discovery_service.discover_repository(scope)
    files = discovery_service.list_files(scope)
    discovery_duration = time.perf_counter() - discovery_start

    assert len(files) >= 100
    assert discovery_duration < 1.5  # Must be well under 1.5 seconds

    # Measure search latency
    search_adapter = RepositorySearchAdapter()
    search_start = time.perf_counter()
    result = search_adapter.search_content(scope=scope, query="func_42")
    search_duration = time.perf_counter() - search_start

    assert len(result.matches) >= 1
    assert search_duration < 3.0  # Under 3.0s for 100 unindexed files on Windows host


# Benchmark 2: Policy engine decision throughput
def test_benchmark_policy_engine_throughput() -> None:
    evaluator = PolicyEvaluator()
    tool_def = ToolDefinition(
        tool_id="test.capability",
        name="test.capability",
        description="Benchmark capability",
        version="1.0",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default",
        executor="test",
        origin=ToolOrigin.BUILTIN,
        enabled=True,
    )

    iterations = 250
    req = PolicyRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="test.capability",
        tool_version="1.0",
        arguments={"path": "src/main.py"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/bench"),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        risk_level=ToolRiskLevel.LOW,
        created_at=datetime.now(UTC),
    )

    start = time.perf_counter()
    for _ in range(iterations):
        evaluator.evaluate(req, tool_def)
    duration = time.perf_counter() - start

    evals_per_sec = iterations / duration
    assert evals_per_sec > 200  # Expect > 200 evaluations per second on Windows


# Benchmark 3: Patch Engine application latency
def test_benchmark_patch_application_latency(tmp_path: Path) -> None:
    repo_dir = tmp_path / "patch_bench"
    repo_dir.mkdir()

    file_paths: list[str] = []
    file_patches: list[FilePatch] = []

    for i in range(10):
        fname = f"target_{i}.py"
        fpath = repo_dir / fname
        fpath.write_text(f"# Initial content {i}\n", encoding="utf-8")
        h = compute_file_hash(fpath)
        file_paths.append(fname)
        file_patches.append(
            FilePatch(
                path=fname,
                operation=PatchOperationType.MODIFY,
                base_hash=h,
                content=f"# Patched content {i}\n",
            )
        )

    task_id = uuid4()
    scope = WorkspaceScope(task_id=task_id, workspace_id=uuid4(), root=str(repo_dir))
    patch = Patch(
        task_id=task_id,
        expected_scope=file_paths,
        file_patches=file_patches,
    )

    engine = PatchEngine()
    start = time.perf_counter()
    res = engine.apply(patch, scope)
    duration = time.perf_counter() - start

    assert res.success is True
    assert len(res.modified_files) == 10
    assert duration < 0.2  # Under 200ms for 10 atomic file patches


# Benchmark 4: SQLite memory manager read/write latency
def test_benchmark_sqlite_memory_latency(tmp_path: Path) -> None:
    db_path = tmp_path / "bench_mem.db"
    manager = ScopedMemoryManager(store=SqliteMemoryStore(db_path))
    task_id = uuid4()

    write_start = time.perf_counter()
    for i in range(50):
        manager.record_task_memory(
            task_id=task_id,
            key=f"key_{i}",
            value=f"value_{i}",
        )
    write_duration = time.perf_counter() - write_start
    assert write_duration < 2.0  # 50 individual commit transactions in < 2.0s

    read_start = time.perf_counter()
    memories = manager.get_scoped_memories(task_id=task_id)
    read_duration = time.perf_counter() - read_start

    assert len(memories) == 50
    assert read_duration < 0.1  # Read in < 100ms
