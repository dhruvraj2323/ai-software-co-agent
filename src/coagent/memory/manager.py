"""Scoped memory manager enforcing project and task boundaries (MCS-001 §16, §17)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from coagent.context.contracts import (
    ContextItem,
    ContextSource,
    Provenance,
    SensitivityClass,
)
from coagent.memory.records import (
    MemoryRecord,
    MemorySource,
    MemoryStatus,
    MemoryType,
)
from coagent.memory.store import MemoryStore, SqliteMemoryStore
from coagent.security.secrets import contains_secret, redact_secrets


class ScopedMemoryManager:
    """Manages memory creation, retrieval, and stale invalidation with scope isolation."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._store = store or SqliteMemoryStore()

    def record_task_memory(
        self,
        task_id: UUID,
        key: str,
        value: Any,
        summary: str | None = None,
        source: MemorySource = MemorySource.OBSERVATION,
        sensitivity: SensitivityClass = SensitivityClass.INTERNAL,
    ) -> MemoryRecord:
        """Record an assumption, constraint, or fact scoped strictly to a single task."""
        # Sanitize sensitive data from memory values
        safe_value = redact_secrets(value) if contains_secret(value) else value

        now = datetime.now(UTC)
        prov = Provenance(
            source_type=ContextSource.TASK_MEMORY,
            source_id=f"task:{task_id}:mem:{key}",
            captured_at=now,
            trust_class="historical_memory",
            freshness=1.0,
        )

        # Check if prior version exists for this key in this task
        existing = self._store.query(
            task_id=task_id,
            memory_type=MemoryType.TASK_MEMORY,
            key=key,
            status=MemoryStatus.ACTIVE,
        )
        version = 1
        for old in existing:
            self._store.update_status(old.memory_id, MemoryStatus.STALE)
            version = max(version, old.version + 1)

        rec = MemoryRecord(
            memory_id=uuid4(),
            type=MemoryType.TASK_MEMORY,
            project_id=None,
            task_id=task_id,
            key=key,
            value=safe_value,
            summary=summary,
            source=source,
            provenance=prov,
            version=version,
            sensitivity=sensitivity,
            status=MemoryStatus.ACTIVE,
        )
        self._store.save(rec)
        return rec

    def record_project_memory(
        self,
        project_id: UUID,
        key: str,
        value: Any,
        summary: str | None = None,
        source: MemorySource = MemorySource.USER,
        sensitivity: SensitivityClass = SensitivityClass.INTERNAL,
    ) -> MemoryRecord:
        """Record a persistent project-wide convention or architectural fact."""
        safe_value = redact_secrets(value) if contains_secret(value) else value

        now = datetime.now(UTC)
        prov = Provenance(
            source_type=ContextSource.PROJECT_MEMORY,
            source_id=f"project:{project_id}:mem:{key}",
            captured_at=now,
            trust_class="historical_memory",
            freshness=1.0,
        )

        existing = self._store.query(
            project_id=project_id,
            memory_type=MemoryType.PROJECT_MEMORY,
            key=key,
            status=MemoryStatus.ACTIVE,
        )
        version = 1
        for old in existing:
            self._store.update_status(old.memory_id, MemoryStatus.STALE)
            version = max(version, old.version + 1)

        rec = MemoryRecord(
            memory_id=uuid4(),
            type=MemoryType.PROJECT_MEMORY,
            project_id=project_id,
            task_id=None,
            key=key,
            value=safe_value,
            summary=summary,
            source=source,
            provenance=prov,
            version=version,
            sensitivity=sensitivity,
            status=MemoryStatus.ACTIVE,
        )
        self._store.save(rec)
        return rec

    def record_decision(
        self,
        key: str,
        decision: Any,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        rationale: str | None = None,
    ) -> MemoryRecord:
        """Record an explicit architectural or technical decision."""
        now = datetime.now(UTC)
        prov = Provenance(
            source_type=ContextSource.PROJECT_MEMORY,
            source_id=f"decision:{key}",
            captured_at=now,
            trust_class="historical_decision",
            freshness=1.0,
        )
        existing = self._store.query(
            project_id=project_id,
            task_id=task_id,
            memory_type=MemoryType.DECISION_MEMORY,
            key=key,
            status=MemoryStatus.ACTIVE,
        )
        version = 1
        for old in existing:
            self._store.update_status(old.memory_id, MemoryStatus.STALE)
            version = max(version, old.version + 1)

        rec = MemoryRecord(
            memory_id=uuid4(),
            type=MemoryType.DECISION_MEMORY,
            project_id=project_id,
            task_id=task_id,
            key=key,
            value={"decision": decision, "rationale": rationale},
            summary=rationale or str(decision),
            source=MemorySource.USER,
            provenance=prov,
            version=version,
            status=MemoryStatus.ACTIVE,
        )
        self._store.save(rec)
        return rec

    def get_scoped_memories(
        self,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        include_stale: bool = False,
    ) -> list[MemoryRecord]:
        """Fetch memories accessible within the current task and project scope.

        Strictly prevents accessing memory belonging to unrelated tasks.
        """
        records: list[MemoryRecord] = []

        # 1. Project-level memories
        if project_id is not None:
            proj_recs = self._store.query(project_id=project_id, task_id=None)
            records.extend(proj_recs)

        # 2. Task-level memories for this specific task only
        if task_id is not None:
            task_recs = self._store.query(task_id=task_id)
            records.extend(task_recs)

        if not include_stale:
            records = [r for r in records if r.status == MemoryStatus.ACTIVE]

        return records

    def invalidate_by_key(
        self,
        key: str,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
    ) -> int:
        """Mark matching active memories as STALE when superseded or contradicted."""
        matches = self._store.query(
            project_id=project_id,
            task_id=task_id,
            key=key,
            status=MemoryStatus.ACTIVE,
        )
        for m in matches:
            self._store.update_status(m.memory_id, MemoryStatus.STALE)
        return len(matches)

    def resolve_conflicts_with_evidence(
        self,
        memories: list[MemoryRecord],
        current_evidence: list[ContextItem],
    ) -> list[MemoryRecord]:
        """Invalidate memories contradicted by current repository evidence (M3, MCS-A07)."""
        valid_memories: list[MemoryRecord] = []

        # Collect current file hashes and status
        current_files = {
            item.provenance.locator: item.hash
            for item in current_evidence
            if item.provenance.locator and item.hash
        }

        for mem in memories:
            loc = mem.provenance.locator
            if loc and loc in current_files:
                curr_hash = current_files[loc]
                if (
                    mem.provenance.source_version
                    and mem.provenance.source_version != curr_hash[:16]
                ):
                    # Underlying file has changed since memory was captured - mark stale
                    self._store.update_status(mem.memory_id, MemoryStatus.STALE)
                    continue

            valid_memories.append(mem)

        return valid_memories
