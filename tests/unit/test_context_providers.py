"""Unit tests for context providers and normalized contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from coagent.context.contracts import (
    AuthorityLayer,
    ContextQuery,
    ContextSource,
    ContextStage,
)
from coagent.context.providers import (
    MemoryContextProvider,
    RepositoryContextProvider,
    TaskContextProvider,
    ValidationContextProvider,
)
from coagent.memory.manager import ScopedMemoryManager
from coagent.memory.store import SqliteMemoryStore
from coagent.workspace.scope import WorkspaceScope


def test_task_context_provider() -> None:
    task_id = uuid4()
    provider = TaskContextProvider(
        {
            "requirement": "Implement user authentication with JWT",
            "plan": "1. Add model\n2. Add endpoint\n3. Add test",
        }
    )

    query = ContextQuery(
        task_id=task_id,
        stage=ContextStage.PLANNING,
    )

    items = provider.provide_context(query)
    assert len(items) == 2
    assert items[0].source_type == ContextSource.TASK
    assert "JWT" in str(items[0].content_or_ref)
    assert items[0].authority_level == int(AuthorityLayer.L1_TASK)


def test_repository_context_provider(tmp_path: Path) -> None:
    task_id = uuid4()
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    target_file = workspace_dir / "app.py"
    target_file.write_text("class App: pass\n", encoding="utf-8")

    scope = WorkspaceScope(
        task_id=task_id,
        workspace_id=uuid4(),
        root=str(workspace_dir),
    )

    provider = RepositoryContextProvider()

    # Query with target_files
    query = ContextQuery(
        task_id=task_id,
        stage=ContextStage.IMPLEMENTATION,
        workspace_scope=scope,
        target_files=["app.py"],
    )

    items = provider.provide_context(query)
    assert len(items) == 1
    assert items[0].source_id == "file:app.py"
    assert "class App" in str(items[0].content_or_ref)
    assert items[0].authority_level == int(AuthorityLayer.L2_REPOSITORY)


def test_validation_context_provider() -> None:
    provider = ValidationContextProvider([
        {"gate": "G4", "status": "FAIL", "error": "ImportError: cannot import name foo"},
    ])

    query = ContextQuery(
        task_id=uuid4(),
        stage=ContextStage.RECOVERY,
    )

    items = provider.provide_context(query)
    assert len(items) == 1
    assert items[0].source_type == ContextSource.VALIDATION
    assert items[0].relevance_score == 1.0  # Max relevance during recovery


def test_memory_context_provider() -> None:
    store = SqliteMemoryStore()
    manager = ScopedMemoryManager(store=store)

    project_id = uuid4()
    task_id = uuid4()

    manager.record_project_memory(
        project_id=project_id,
        key="naming_convention",
        value="Use snake_case for functions",
    )
    manager.record_task_memory(
        task_id=task_id,
        key="temp_assumption",
        value="Database is in SQLite mode",
    )

    provider = MemoryContextProvider(memory_manager=manager, project_id=project_id)

    query = ContextQuery(
        task_id=task_id,
        stage=ContextStage.PLANNING,
    )

    items = provider.provide_context(query)
    assert len(items) == 2
    sources = {i.source_type for i in items}
    assert ContextSource.PROJECT_MEMORY in sources
    assert ContextSource.TASK_MEMORY in sources

