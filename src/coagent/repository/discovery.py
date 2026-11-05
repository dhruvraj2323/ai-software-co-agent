"""Repository discovery and scope identification service."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

from coagent.security.path import require_path_within_workspace
from coagent.workspace.scope import WorkspaceScope

DEFAULT_IGNORED_DIRS: frozenset[str] = frozenset({
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".tox",
    ".idea",
    ".vscode",
    "dist",
    "build",
})

DEFAULT_IGNORED_PATTERNS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dylib",
    "*.dll",
    ".DS_Store",
    "Thumbs.db",
)


@dataclass(frozen=True)
class RepositoryInfo:
    """Safe metadata describing an identified repository within a workspace."""

    root_path: Path
    is_git_repository: bool
    workspace_scope: WorkspaceScope
    relative_to_workspace: str


class RepositoryDiscoveryService:
    """Safely discovers repository boundaries, ignoring out-of-scope paths."""

    def __init__(
        self,
        ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS,
        ignored_patterns: tuple[str, ...] = DEFAULT_IGNORED_PATTERNS,
        max_scan_files: int = 10_000,
    ) -> None:
        self._ignored_dirs = ignored_dirs
        self._ignored_patterns = ignored_patterns
        self._max_scan_files = max_scan_files

    def discover_repository(
        self,
        scope: WorkspaceScope,
        start_path: str | Path | None = None,
    ) -> RepositoryInfo:
        """Discover the repository root starting from a workspace directory.

        Traverses upwards from start_path towards the authorized workspace root.
        Strictly halts at workspace root boundary: it will NEVER inspect or return
        paths outside the authorized workspace scope.
        """
        workspace_root = Path(scope.root).resolve()

        if start_path is None:
            current = workspace_root
        else:
            current = require_path_within_workspace(scope, str(start_path))

        is_git = False
        repo_root = workspace_root

        # Traverse upwards from current to workspace_root looking for .git
        probe = current
        while True:
            # Check if probe is within workspace root
            try:
                probe.relative_to(workspace_root)
            except ValueError:
                break

            git_marker = probe / ".git"
            if git_marker.exists():
                repo_root = probe
                is_git = True
                break

            if probe == workspace_root or probe.parent == probe:
                break
            probe = probe.parent

        rel_path = str(repo_root.relative_to(workspace_root))
        if rel_path == ".":
            rel_path = ""

        return RepositoryInfo(
            root_path=repo_root,
            is_git_repository=is_git,
            workspace_scope=scope,
            relative_to_workspace=rel_path,
        )

    def list_files(
        self,
        scope: WorkspaceScope,
        subpath: str | Path | None = None,
        include_ignored: bool = False,
    ) -> list[Path]:
        """List files in the repository respecting workspace bounds and ignore rules.

        Returns canonical resolved Paths that strictly reside within the workspace.
        """
        if subpath is None:
            scan_dir = Path(scope.root).resolve()
        else:
            scan_dir = require_path_within_workspace(scope, str(subpath))

        if not scan_dir.exists():
            return []

        if scan_dir.is_file():
            return [scan_dir]

        gitignore_rules = self._load_gitignore_rules(scan_dir, Path(scope.root).resolve())

        found_files: list[Path] = []

        for root, dirs, files in scan_dir.walk():
            # In-place modify dirs to prevent descending into ignored directories
            if not include_ignored:
                dirs[:] = [
                    d for d in dirs
                    if d not in self._ignored_dirs and not d.startswith(".git")
                ]

            for file_name in files:
                if len(found_files) >= self._max_scan_files:
                    return found_files

                if not include_ignored and self._is_pattern_ignored(file_name):
                    continue

                full_path = root / file_name
                # Verify safety
                try:
                    full_path.resolve().relative_to(Path(scope.root).resolve())
                except ValueError:
                    # Traversal or escaped symlink - skip
                    continue

                if not include_ignored and self._is_path_gitignore_ignored(
                    full_path, scan_dir, gitignore_rules
                ):
                    continue

                found_files.append(full_path)

        return found_files

    def _is_pattern_ignored(self, filename: str) -> bool:
        return any(fnmatch.fnmatch(filename, pattern) for pattern in self._ignored_patterns)

    def _load_gitignore_rules(self, base_dir: Path, workspace_root: Path) -> list[str]:
        rules: list[str] = []
        current = base_dir
        while True:
            gi_file = current / ".gitignore"
            if gi_file.is_file():
                try:
                    for line in gi_file.read_text(encoding="utf-8", errors="replace").splitlines():
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#"):
                            rules.append(stripped)
                except OSError:
                    pass
            if current == workspace_root or current.parent == current:
                break
            current = current.parent
        return rules

    def _is_path_gitignore_ignored(self, path: Path, base_dir: Path, rules: list[str]) -> bool:
        if not rules:
            return False
        try:
            rel = str(path.relative_to(base_dir)).replace("\\", "/")
        except ValueError:
            return False

        for rule in rules:
            normalized_rule = rule.strip("/")
            if fnmatch.fnmatch(rel, normalized_rule) or fnmatch.fnmatch(path.name, normalized_rule):
                return True
            if fnmatch.fnmatch(rel, f"{normalized_rule}/*"):
                return True
        return False
