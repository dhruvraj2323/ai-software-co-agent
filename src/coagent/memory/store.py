"""Persistent SQLite storage implementation for structured memory records."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Protocol
from uuid import UUID

from coagent.memory.records import MemoryRecord, MemoryStatus, MemoryType


class MemoryStore(Protocol):
    """Protocol for memory persistence engines."""

    def save(self, record: MemoryRecord) -> None:
        """Persist or update a memory record."""
        ...

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory record by its primary identity."""
        ...

    def query(
        self,
        *,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        memory_type: MemoryType | None = None,
        key: str | None = None,
        status: MemoryStatus | None = None,
    ) -> list[MemoryRecord]:
        """Query memory records with scope and type filters."""
        ...

    def update_status(self, memory_id: UUID, status: MemoryStatus) -> None:
        """Update the lifecycle status of an existing record."""
        ...

    def delete(self, memory_id: UUID) -> bool:
        """Permanently delete a memory record."""
        ...


class SqliteMemoryStore:
    """SQLite-backed memory store providing transaction-safe persistence."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    memory_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    project_id TEXT,
                    task_id TEXT,
                    key TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_scope ON memory_records(project_id, task_id)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_key ON memory_records(key)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_type ON memory_records(type, status)"
            )

    def save(self, record: MemoryRecord) -> None:
        raw_json = record.model_dump_json()
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO memory_records (
                    memory_id, type, project_id, task_id, key, data_json,
                    status, version, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(record.memory_id),
                    record.type.value,
                    str(record.project_id) if record.project_id else None,
                    str(record.task_id) if record.task_id else None,
                    record.key,
                    raw_json,
                    record.status.value,
                    record.version,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ),
            )

    def get(self, memory_id: UUID) -> MemoryRecord | None:
        row = self._conn.execute(
            "SELECT data_json FROM memory_records WHERE memory_id = ?",
            (str(memory_id),),
        ).fetchone()
        if row is None:
            return None
        return MemoryRecord.model_validate_json(row["data_json"])

    def query(
        self,
        *,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        memory_type: MemoryType | None = None,
        key: str | None = None,
        status: MemoryStatus | None = None,
    ) -> list[MemoryRecord]:
        query_sql = "SELECT data_json FROM memory_records WHERE 1=1"
        params: list[str] = []

        if project_id is not None:
            query_sql += " AND project_id = ?"
            params.append(str(project_id))
        if task_id is not None:
            query_sql += " AND task_id = ?"
            params.append(str(task_id))
        if memory_type is not None:
            query_sql += " AND type = ?"
            params.append(memory_type.value)
        if key is not None:
            query_sql += " AND key = ?"
            params.append(key)
        if status is not None:
            query_sql += " AND status = ?"
            params.append(status.value)

        query_sql += " ORDER BY created_at DESC"
        rows = self._conn.execute(query_sql, params).fetchall()

        return [MemoryRecord.model_validate_json(r["data_json"]) for r in rows]

    def update_status(self, memory_id: UUID, status: MemoryStatus) -> None:
        rec = self.get(memory_id)
        if rec is None:
            return
        updated_rec = rec.model_copy(update={"status": status})
        self.save(updated_rec)

    def delete(self, memory_id: UUID) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM memory_records WHERE memory_id = ?",
                (str(memory_id),),
            )
            return cur.rowcount > 0

    def close(self) -> None:
        self._conn.close()
