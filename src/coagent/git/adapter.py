"""Controlled Git CLI adapter for status, diffs, checkpoints, and rollbacks (T045)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import UUID

from coagent.git.status import GitStatus


class GitExecutionError(RuntimeError):
    """Raised when a Git command returns a non-zero exit code."""

    def __init__(self, command: list[str], exit_code: int, stderr: str) -> None:
        super().__init__(f"Git command {' '.join(command)} failed ({exit_code}): {stderr}")
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr


class GitAdapter:
    """Safe, controlled interface for workspace Git operations."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = Path(workspace_root).resolve()

    def _run(self, args: list[str], check: bool = True) -> str:
        """Run a git command strictly within the workspace root."""
        cmd = ["git", *args]
        result = subprocess.run(
            cmd,
            cwd=str(self._root),
            capture_output=True,
            text=True,
            check=False,
        )
        if check and result.returncode != 0:
            raise GitExecutionError(cmd, result.returncode, result.stderr.strip())
        return result.stdout.strip()

    def is_git_repository(self) -> bool:
        """Return True if the workspace root is inside a valid git work tree."""
        try:
            res = self._run(["rev-parse", "--is-inside-work-tree"], check=False)
            return res == "true"
        except Exception:
            return False

    def get_status(self) -> GitStatus:
        """Return structured Git status."""
        if not self.is_git_repository():
            return GitStatus(is_clean=True)

        branch = self._run(["rev-parse", "--abbrev-ref", "HEAD"], check=False) or "HEAD"
        commit_hash = self._run(["rev-parse", "HEAD"], check=False) or None

        cmd = ["git", "status", "--porcelain=v1"]
        res = subprocess.run(
            cmd,
            cwd=str(self._root),
            capture_output=True,
            text=True,
            check=False,
        )

        staged: list[str] = []
        modified: list[str] = []
        untracked: list[str] = []

        for line in res.stdout.splitlines():
            if len(line) < 4:
                continue
            x = line[0]
            y = line[1]
            path = line[3:].strip()
            if x == "?" and y == "?":
                untracked.append(path)
            else:
                if x in "MADRC":
                    staged.append(path)
                if y in "MD":
                    modified.append(path)

        is_clean = not bool(staged or modified or untracked)
        return GitStatus(
            branch=branch,
            commit_hash=commit_hash,
            is_clean=is_clean,
            staged_files=staged,
            modified_files=modified,
            untracked_files=untracked,
        )

    def get_diff(self, path: str | None = None) -> str:
        """Return unified diff of unstaged and staged changes."""
        if not self.is_git_repository():
            return ""

        args = ["diff", "HEAD"]
        if path:
            args.extend(["--", path])

        return self._run(args, check=False)

    def create_checkpoint(self, task_id: UUID) -> str:
        """Create a checkpoint stash or ref representing pre-task baseline."""
        if not self.is_git_repository():
            return "no-git"

        checkpoint_name = f"coagent-task-{task_id}"
        # Stash untracked and modified changes with a deterministic message
        self._run(["stash", "push", "--include-untracked", "-m", checkpoint_name])
        return checkpoint_name

    def rollback(self) -> bool:
        """Safely restore working tree to HEAD, discarding task modifications."""
        if not self.is_git_repository():
            return False

        self._run(["reset", "--hard", "HEAD"])
        self._run(["clean", "-fd"])
        return True
