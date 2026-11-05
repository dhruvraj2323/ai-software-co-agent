"""Benchmark and relevance test for Context Assembly & Budgeting (T064)."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

from coagent.context.budget import ContextBudget
from coagent.context.contracts import ContextQuery, ContextStage
from coagent.context.engine import ContextEngine
from coagent.context.providers import (
    MemoryContextProvider,
    RepositoryContextProvider,
    TaskContextProvider,
    ValidationContextProvider,
)
from coagent.memory.manager import ScopedMemoryManager
from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.map import RepositoryMapService
from coagent.workspace.scope import WorkspaceScope


def test_context_relevance_and_budget_benchmark(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "bench_workspace"
    workspace_dir.mkdir()

    # Create multiple files
    for i in range(20):
        (workspace_dir / f"service_{i}.py").write_text(
            f"class Service{i}:\n    '''Docstring for service {i}'''\n    def run(self): pass\n",
            encoding="utf-8",
        )

    task_id = uuid4()
    project_id = uuid4()

    scope = WorkspaceScope(
        task_id=task_id,
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    task_prov = TaskContextProvider({
        "requirement": "Refactor Service1 and Service2 to use common base",
        "plan": "1. Extract base\n2. Inherit base\n3. Run tests",
    })

    discovery = RepositoryDiscoveryService()
    map_service = RepositoryMapService(discovery_service=discovery)
    repo_prov = RepositoryContextProvider(map_service=map_service)

    val_prov = ValidationContextProvider([
        {"test": "test_service_1", "status": "FAIL", "message": "AssertionError"},
        {"test": "test_service_2", "status": "PASS", "message": "OK"},
    ])

    mem_mgr = ScopedMemoryManager()
    mem_mgr.record_project_memory(
        project_id=project_id,
        key="conventions",
        value="Use type annotations everywhere",
    )
    mem_mgr.record_task_memory(
        task_id=task_id,
        key="assumption",
        value="Service1 is deprecated",
    )
    mem_prov = MemoryContextProvider(memory_manager=mem_mgr, project_id=project_id)

    engine = ContextEngine(
        providers=[task_prov, repo_prov, val_prov, mem_prov],
        budget=ContextBudget(
            max_total_tokens=2000,
            max_total_items=10,
        ),
    )

    query = ContextQuery(
        task_id=task_id,
        stage=ContextStage.RECOVERY,
        workspace_scope=scope,
        target_files=["service_1.py", "service_2.py"],
    )

    start_t = time.perf_counter()
    pkg = engine.assemble_context(query)
    duration = time.perf_counter() - start_t

    # Verification of performance and budget invariants
    assert duration < 1.0  # Must be fast
    assert pkg.manifest.total_tokens <= 2000  # Strict budget ceiling
    assert len(pkg.items) <= 10  # Item count ceiling

    # In RECOVERY stage, validation outcome must be present
    sources_in_pkg = {item.source_type for item in pkg.items}
    assert "VALIDATION" in [s.value for s in sources_in_pkg]
    assert pkg.manifest.task_id == task_id
    assert pkg.manifest.stage == "RECOVERY"

