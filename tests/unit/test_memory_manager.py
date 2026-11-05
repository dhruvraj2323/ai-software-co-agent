"""Unit tests for SQLite memory store and scoped memory manager."""

from __future__ import annotations

from uuid import uuid4

from coagent.context.contracts import ContextItem, ContextSource, Provenance
from coagent.memory.manager import ScopedMemoryManager
from coagent.memory.records import MemoryRecord, MemoryStatus, MemoryType
from coagent.memory.store import SqliteMemoryStore


def test_sqlite_memory_store_crud() -> None:
    store = SqliteMemoryStore()
    mem_id = uuid4()
    proj_id = uuid4()

    record = MemoryRecord(
        memory_id=mem_id,
        type=MemoryType.PROJECT_MEMORY,
        project_id=proj_id,
        task_id=None,
        key="db_type",
        value={"driver": "sqlite3"},
        summary="Database type is sqlite",
        source="SYSTEM",  # type: ignore[arg-type]
        provenance=Provenance(source_type=ContextSource.PROJECT_MEMORY, source_id="sys:1"),
        version=1,
        status=MemoryStatus.ACTIVE,
    )

    store.save(record)

    loaded = store.get(mem_id)
    assert loaded is not None
    assert loaded.key == "db_type"
    assert loaded.value == {"driver": "sqlite3"}

    # Update status
    store.update_status(mem_id, MemoryStatus.STALE)
    loaded_stale = store.get(mem_id)
    assert loaded_stale is not None
    assert loaded_stale.status == MemoryStatus.STALE

    # Delete
    assert store.delete(mem_id) is True
    assert store.get(mem_id) is None


def test_scoped_memory_manager_isolation() -> None:
    manager = ScopedMemoryManager()

    project_id = uuid4()
    task_a = uuid4()
    task_b = uuid4()

    # Task A memory
    manager.record_task_memory(task_id=task_a, key="step", value="step 1 done")
    # Task B memory
    manager.record_task_memory(task_id=task_b, key="step", value="step 2 done")
    # Project memory
    manager.record_project_memory(project_id=project_id, key="arch", value="microservices")

    # Scope for Task A must NOT see Task B's memory
    memories_a = manager.get_scoped_memories(project_id=project_id, task_id=task_a)
    keys_a = {m.key for m in memories_a}
    values_a = {str(m.value) for m in memories_a}

    assert "step" in keys_a
    assert "arch" in keys_a
    assert "step 1 done" in values_a
    assert "step 2 done" not in values_a  # Task B's private memory is isolated


def test_scoped_memory_versioning_and_stale() -> None:
    manager = ScopedMemoryManager()
    task_id = uuid4()

    rec1 = manager.record_task_memory(task_id=task_id, key="counter", value=1)
    assert rec1.version == 1
    assert rec1.status == MemoryStatus.ACTIVE

    # Update key
    rec2 = manager.record_task_memory(task_id=task_id, key="counter", value=2)
    assert rec2.version == 2
    assert rec2.status == MemoryStatus.ACTIVE

    # rec1 should be marked STALE
    old = manager._store.get(rec1.memory_id)
    assert old is not None
    assert old.status == MemoryStatus.STALE


def test_conflict_resolution_with_current_evidence() -> None:
    manager = ScopedMemoryManager()
    task_id = uuid4()

    # Memory says file hash was 'oldhash'
    mem = manager.record_task_memory(task_id=task_id, key="cached_model", value="OldModel")
    # Set locator and version on memory
    mem.provenance.locator = "src/models.py"
    mem.provenance.source_version = "oldhash"
    manager._store.save(mem)

    # Current repo evidence has 'newhash'
    current_evidence = [
        ContextItem(
            source_type=ContextSource.REPOSITORY,
            source_id="file:src/models.py",
            content_or_ref="class NewModel: pass",
            provenance=Provenance(
                source_type=ContextSource.REPOSITORY,
                source_id="file:src/models.py",
                locator="src/models.py",
            ),
            hash="newhash1234567890",
        )
    ]

    active_mems = manager.get_scoped_memories(task_id=task_id)
    resolved = manager.resolve_conflicts_with_evidence(active_mems, current_evidence)

    # Contradicted stale memory is excluded
    assert len(resolved) == 0
    updated_mem = manager._store.get(mem.memory_id)
    assert updated_mem is not None
    assert updated_mem.status == MemoryStatus.STALE

