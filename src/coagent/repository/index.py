"""Repository indexing and metadata persistence."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.symbols import SymbolInfo, SymbolRegistry
from coagent.security.path import require_path_within_workspace
from coagent.workspace.scope import WorkspaceScope


@dataclass(frozen=True)
class IndexedFile:
    """Record of an indexed file in the repository."""

    relative_path: str
    sha256: str
    size_bytes: int
    mtime: float


class RepositoryIndex:
    """SQLite-backed index of repository files, hashes, and code symbols."""

    def __init__(
        self,
        db_path: Path | str = ":memory:",
        symbol_registry: SymbolRegistry | None = None,
        discovery_service: RepositoryDiscoveryService | None = None,
    ) -> None:
        self._db_path = str(db_path)
        self._symbols = symbol_registry or SymbolRegistry()
        self._discovery = discovery_service or RepositoryDiscoveryService()
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    relative_path TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    mtime REAL NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER NOT NULL,
                    signature TEXT,
                    docstring TEXT,
                    parent_symbol TEXT,
                    FOREIGN KEY(file_path) REFERENCES files(relative_path) ON DELETE CASCADE
                )
                """
            )
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol_name ON symbols(name)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol_file ON symbols(file_path)")

    def index_workspace(self, scope: WorkspaceScope, subpath: str | Path | None = None) -> int:
        """Scan workspace and update index incrementally. Returns count of indexed files."""
        files = self._discovery.list_files(scope, subpath=subpath)
        workspace_root = Path(scope.root).resolve()

        updated_count = 0
        for file_path in files:
            rel = str(file_path.relative_to(workspace_root)).replace("\\", "/")
            if self._update_file_if_changed(file_path, rel):
                updated_count += 1
        return updated_count

    def _update_file_if_changed(self, file_path: Path, rel_path: str) -> bool:
        try:
            st = file_path.stat()
        except OSError:
            return False

        cur = self._conn.cursor()
        row = cur.execute(
            "SELECT sha256, mtime, size_bytes FROM files WHERE relative_path = ?",
            (rel_path,),
        ).fetchone()

        if row is not None and row["mtime"] == st.st_mtime and row["size_bytes"] == st.st_size:
            return False

        # File is new or changed: compute hash and extract symbols
        try:
            content_bytes = file_path.read_bytes()
        except OSError:
            return False

        sha256 = hashlib.sha256(content_bytes).hexdigest()
        if row is not None and row["sha256"] == sha256:
            # Only mtime touched, content identical
            with self._conn:
                self._conn.execute(
                    "UPDATE files SET mtime = ?, size_bytes = ? WHERE relative_path = ?",
                    (st.st_mtime, st.st_size, rel_path),
                )
            return False

        try:
            text = content_bytes.decode("utf-8", errors="replace")
        except Exception:
            text = ""

        symbols = self._symbols.extract_symbols(file_path, content=text)

        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO files (relative_path, sha256, size_bytes, mtime)
                VALUES (?, ?, ?, ?)
                """,
                (rel_path, sha256, st.st_size, st.st_mtime),
            )
            self._conn.execute("DELETE FROM symbols WHERE file_path = ?", (rel_path,))
            for sym in symbols:
                self._conn.execute(
                    """
                    INSERT INTO symbols (
                        file_path, name, kind, line_start, line_end,
                        signature, docstring, parent_symbol
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rel_path,
                        sym.name,
                        sym.kind.value,
                        sym.line_start,
                        sym.line_end,
                        sym.signature,
                        sym.docstring,
                        sym.parent_symbol,
                    ),
                )
        return True

    def get_file(self, relative_path: str) -> IndexedFile | None:
        row = self._conn.execute(
            "SELECT relative_path, sha256, size_bytes, mtime FROM files WHERE relative_path = ?",
            (relative_path.replace("\\", "/"),),
        ).fetchone()
        if row is None:
            return None
        return IndexedFile(
            relative_path=row["relative_path"],
            sha256=row["sha256"],
            size_bytes=row["size_bytes"],
            mtime=row["mtime"],
        )

    def is_fresh(self, scope: WorkspaceScope, relative_path: str) -> bool:
        """Check if index record matches actual file on disk."""
        target = require_path_within_workspace(scope, relative_path)
        if not target.exists():
            return False
        rec = self.get_file(relative_path)
        if rec is None:
            return False
        try:
            content_bytes = target.read_bytes()
            sha256 = hashlib.sha256(content_bytes).hexdigest()
            return rec.sha256 == sha256
        except OSError:
            return False

    def invalidate(self, relative_path: str) -> None:
        """Invalidate index entries for a file."""
        norm = relative_path.replace("\\", "/")
        with self._conn:
            self._conn.execute("DELETE FROM symbols WHERE file_path = ?", (norm,))
            self._conn.execute("DELETE FROM files WHERE relative_path = ?", (norm,))

    def get_symbols_for_file(self, relative_path: str) -> list[SymbolInfo]:
        rows = self._conn.execute(
            """
            SELECT name, kind, line_start, line_end, signature, docstring, parent_symbol
            FROM symbols WHERE file_path = ? ORDER BY line_start ASC
            """,
            (relative_path.replace("\\", "/"),),
        ).fetchall()

        from coagent.repository.symbols import SymbolKind

        return [
            SymbolInfo(
                name=r["name"],
                kind=SymbolKind(r["kind"]),
                file_path=relative_path,
                line_start=r["line_start"],
                line_end=r["line_end"],
                signature=r["signature"],
                docstring=r["docstring"],
                parent_symbol=r["parent_symbol"],
            )
            for r in rows
        ]

    def find_symbols(self, name_query: str) -> list[SymbolInfo]:
        from coagent.repository.symbols import SymbolKind

        pattern = f"%{name_query}%"
        rows = self._conn.execute(
            """
            SELECT file_path, name, kind, line_start, line_end, signature, docstring, parent_symbol
            FROM symbols WHERE name LIKE ? ORDER BY name ASC LIMIT 100
            """,
            (pattern,),
        ).fetchall()

        return [
            SymbolInfo(
                name=r["name"],
                kind=SymbolKind(r["kind"]),
                file_path=r["file_path"],
                line_start=r["line_start"],
                line_end=r["line_end"],
                signature=r["signature"],
                docstring=r["docstring"],
                parent_symbol=r["parent_symbol"],
            )
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()
