"""Scoped repository file and content search adapter."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

from coagent.repository.discovery import RepositoryDiscoveryService
from coagent.security.path import require_path_within_workspace
from coagent.security.policy import ProtectedPathCategory, ProtectedPathPolicy
from coagent.workspace.scope import WorkspaceScope


@dataclass(frozen=True)
class SearchMatch:
    """Individual match within a file."""

    path: Path
    relative_path: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int


@dataclass(frozen=True)
class SearchResult:
    """Outcome of a repository search query."""

    matches: list[SearchMatch]
    total_matches: int
    truncated: bool
    searched_files_count: int


class RepositorySearchAdapter:
    """Safe, scoped search across repository file names and contents."""

    def __init__(
        self,
        discovery_service: RepositoryDiscoveryService | None = None,
        path_policy: ProtectedPathPolicy | None = None,
    ) -> None:
        self._discovery = discovery_service or RepositoryDiscoveryService()
        self._policy = path_policy or ProtectedPathPolicy()

    def find_files(
        self,
        scope: WorkspaceScope,
        pattern: str,
        subpath: str | Path | None = None,
        max_results: int = 500,
    ) -> list[Path]:
        """Find files matching a glob pattern strictly within workspace scope."""
        all_files = self._discovery.list_files(scope, subpath=subpath)
        workspace_root = Path(scope.root).resolve()

        results: list[Path] = []
        for file_path in all_files:
            rel = str(file_path.relative_to(workspace_root)).replace("\\", "/")
            if fnmatch.fnmatch(file_path.name, pattern) or fnmatch.fnmatch(rel, pattern):
                results.append(file_path)
                if len(results) >= max_results:
                    break
        return results

    def search_content(
        self,
        scope: WorkspaceScope,
        query: str,
        subpath: str | Path | None = None,
        is_regex: bool = False,
        case_sensitive: bool = True,
        file_pattern: str | None = None,
        max_matches: int = 500,
        max_file_size_bytes: int = 2 * 1024 * 1024,  # 2MB max per searched file
    ) -> SearchResult:
        """Search content across repository files within the workspace.

        Filters out protected secret paths and binary/oversized files.
        """
        # Validate search target path
        if subpath is not None:
            require_path_within_workspace(scope, str(subpath))

        all_files = self._discovery.list_files(scope, subpath=subpath)
        workspace_root = Path(scope.root).resolve()

        flags = 0 if case_sensitive else re.IGNORECASE
        if is_regex:
            compiled_regex = re.compile(query, flags)
        else:
            compiled_regex = re.compile(re.escape(query), flags)

        matches: list[SearchMatch] = []
        searched_files = 0
        truncated = False

        for file_path in all_files:
            # Skip protected secret files to prevent credential leakage
            category = self._policy.classify(scope, str(file_path))
            if category == ProtectedPathCategory.SECRETS:
                continue

            # Check file pattern filter if specified
            if file_pattern and not fnmatch.fnmatch(file_path.name, file_pattern):
                continue

            try:
                st = file_path.stat()
                if st.st_size > max_file_size_bytes:
                    continue
            except OSError:
                continue

            searched_files += 1
            rel_path = str(file_path.relative_to(workspace_root)).replace("\\", "/")

            try:
                # Read as utf-8, skipping binaries
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                # Search for match in line
                m = compiled_regex.search(line)
                if m:
                    matches.append(
                        SearchMatch(
                            path=file_path,
                            relative_path=rel_path,
                            line_number=line_no,
                            line_content=line[:200],  # Bound line preview length
                            match_start=m.start(),
                            match_end=m.end(),
                        )
                    )
                    if len(matches) >= max_matches:
                        truncated = True
                        break
            if truncated:
                break

        return SearchResult(
            matches=matches,
            total_matches=len(matches),
            truncated=truncated,
            searched_files_count=searched_files,
        )
