"""Compact repository structure map for agent reasoning context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.repository.index import RepositoryIndex
from coagent.workspace.scope import WorkspaceScope


@dataclass(frozen=True)
class RepositoryMap:
    """Rendered repository structure summary with estimated size."""

    content: str
    file_count: int
    directory_count: int
    token_estimate: int


class RepositoryMapService:
    """Generates compact, structured repository outlines for model reasoning."""

    def __init__(
        self,
        discovery_service: RepositoryDiscoveryService | None = None,
        index: RepositoryIndex | None = None,
    ) -> None:
        self._discovery = discovery_service or RepositoryDiscoveryService()
        self._index = index

    def generate_map(
        self,
        scope: WorkspaceScope,
        subpath: str | Path | None = None,
        max_depth: int = 4,
        max_tokens: int = 2000,
        include_symbols: bool = True,
    ) -> RepositoryMap:
        """Construct a compact text outline of the repository files and key symbols."""
        files = self._discovery.list_files(scope, subpath=subpath)
        workspace_root = Path(scope.root).resolve()

        # Build directory tree
        tree: dict[str, list[str]] = {}
        dir_set: set[str] = set()

        for file_path in files:
            rel = file_path.relative_to(workspace_root)
            parts = rel.parts
            if len(parts) > max_depth + 1:
                # Truncate depth
                dir_key = "/".join(parts[:max_depth])
                tree.setdefault(dir_key, [])
                dir_set.add(dir_key)
                continue

            dir_key = "/".join(parts[:-1]) if len(parts) > 1 else ""
            tree.setdefault(dir_key, []).append(parts[-1])
            if dir_key:
                dir_set.add(dir_key)

        lines: list[str] = [f"Repository Root: {workspace_root.name}/"]
        char_count = len(lines[0])
        max_chars = max_tokens * 4

        # Render tree deterministically
        for dir_key in sorted(tree.keys()):
            prefix = f"{dir_key}/" if dir_key else "./"
            dir_header = f"\n[{prefix}]"
            lines.append(dir_header)
            char_count += len(dir_header)

            for file_name in sorted(tree[dir_key]):
                if char_count >= max_chars:
                    lines.append("  ... (truncated due to token budget)")
                    break

                rel_file = f"{dir_key}/{file_name}" if dir_key else file_name
                symbols_summary = ""
                if include_symbols and self._index is not None and file_name.endswith(".py"):
                    syms = self._index.get_symbols_for_file(rel_file)
                    classes = [s.name for s in syms if s.kind.value == "CLASS"]
                    funcs = [s.name for s in syms if s.kind.value == "FUNCTION"]
                    sym_parts: list[str] = []
                    if classes:
                        sym_parts.append(f"classes: {', '.join(classes[:3])}")
                    if funcs:
                        sym_parts.append(f"funcs: {', '.join(funcs[:3])}")
                    if sym_parts:
                        symbols_summary = f" ({'; '.join(sym_parts)})"

                file_line = f"  - {file_name}{symbols_summary}"
                lines.append(file_line)
                char_count += len(file_line)

            if char_count >= max_chars:
                break

        full_content = "\n".join(lines)
        token_est = max(1, len(full_content) // 4)

        return RepositoryMap(
            content=full_content,
            file_count=len(files),
            directory_count=len(dir_set),
            token_estimate=token_est,
        )
