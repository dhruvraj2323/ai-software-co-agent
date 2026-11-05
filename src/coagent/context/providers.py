"""Context provider interface and implementations for runtime subsystems."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from coagent.context.contracts import (
    AuthorityLayer,
    ContextItem,
    ContextQuery,
    ContextSource,
    ContextStage,
    Provenance,
    SensitivityClass,
)
from coagent.git.adapter import GitAdapter
from coagent.repository.map import RepositoryMapService
from coagent.security.path import is_path_within_workspace
from coagent.workspace.paths import resolve_workspace_path
from coagent.workspace.scope import WorkspaceScope

if TYPE_CHECKING:
    from coagent.memory.manager import ScopedMemoryManager


class ContextProvider(Protocol):
    """Protocol for sources contributing normalized context items."""

    @property
    def name(self) -> str:
        """Descriptive provider name."""
        ...

    @property
    def source_type(self) -> ContextSource:
        """Category of context produced."""
        ...

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        """Produce normalized context items relevant to the query."""
        ...


class TaskContextProvider:
    """Provides requirement, scope, and plan context from task state."""

    def __init__(self, task_metadata: dict[str, Any] | None = None) -> None:
        self._metadata = task_metadata or {}

    @property
    def name(self) -> str:
        return "task_provider"

    @property
    def source_type(self) -> ContextSource:
        return ContextSource.TASK

    def update_task_metadata(self, metadata: dict[str, Any]) -> None:
        self._metadata.update(metadata)

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        items: list[ContextItem] = []
        now = datetime.now(UTC)

        requirement = self._metadata.get("requirement", "")
        if requirement:
            prov = Provenance(
                source_type=ContextSource.TASK,
                source_id=f"task:{query.task_id}:requirement",
                captured_at=now,
                trust_class="task_intent",
                freshness=1.0,
            )
            items.append(
                ContextItem(
                    source_type=ContextSource.TASK,
                    source_id=prov.source_id,
                    content_or_ref=str(requirement),
                    summary="Task requirement and acceptance criteria",
                    relevance_score=1.0,
                    freshness_score=1.0,
                    authority_level=int(AuthorityLayer.L1_TASK),
                    provenance=prov,
                    sensitivity=SensitivityClass.INTERNAL,
                    token_estimate=max(1, len(str(requirement)) // 4),
                )
            )

        plan = self._metadata.get("plan")
        if plan:
            prov = Provenance(
                source_type=ContextSource.TASK,
                source_id=f"task:{query.task_id}:plan",
                captured_at=now,
                trust_class="task_intent",
                freshness=1.0,
            )
            plan_str = str(plan)
            items.append(
                ContextItem(
                    source_type=ContextSource.TASK,
                    source_id=prov.source_id,
                    content_or_ref=plan_str,
                    summary="Execution plan",
                    relevance_score=0.9,
                    freshness_score=1.0,
                    authority_level=int(AuthorityLayer.L1_TASK),
                    provenance=prov,
                    sensitivity=SensitivityClass.INTERNAL,
                    token_estimate=max(1, len(plan_str) // 4),
                )
            )

        return items


class RepositoryContextProvider:
    """Provides repository map and targeted file context."""

    def __init__(self, map_service: RepositoryMapService | None = None) -> None:
        self._map_service = map_service or RepositoryMapService()

    @property
    def name(self) -> str:
        return "repository_provider"

    @property
    def source_type(self) -> ContextSource:
        return ContextSource.REPOSITORY

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        items: list[ContextItem] = []
        now = datetime.now(UTC)

        if query.workspace_scope is None:
            return items

        scope: WorkspaceScope = query.workspace_scope

        # Include repository map for understanding and planning stages
        if query.stage in {ContextStage.UNDERSTANDING, ContextStage.PLANNING}:
            repo_map = self._map_service.generate_map(scope, max_tokens=1500)
            map_hash = hashlib.sha256(repo_map.content.encode("utf-8")).hexdigest()
            prov = Provenance(
                source_type=ContextSource.REPOSITORY,
                source_id="repository:map",
                source_version=map_hash[:16],
                captured_at=now,
                trust_class="current_evidence",
                freshness=1.0,
            )
            items.append(
                ContextItem(
                    source_type=ContextSource.REPOSITORY,
                    source_id="repository:map",
                    content_or_ref=repo_map.content,
                    summary=f"Repository outline ({repo_map.file_count} files)",
                    relevance_score=0.95,
                    freshness_score=1.0,
                    authority_level=int(AuthorityLayer.L2_REPOSITORY),
                    provenance=prov,
                    token_estimate=repo_map.token_estimate,
                    hash=map_hash,
                )
            )

        # Include specific target files if requested
        for target_file in query.target_files:
            if not is_path_within_workspace(scope, target_file):
                continue
            resolved = resolve_workspace_path(scope, target_file)
            if resolved.is_file():
                try:
                    content = resolved.read_text(encoding="utf-8", errors="replace")
                    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    prov = Provenance(
                        source_type=ContextSource.REPOSITORY,
                        source_id=f"file:{target_file}",
                        source_version=file_hash[:16],
                        captured_at=now,
                        locator=target_file,
                        trust_class="current_evidence",
                        freshness=1.0,
                    )
                    items.append(
                        ContextItem(
                            source_type=ContextSource.REPOSITORY,
                            source_id=f"file:{target_file}",
                            content_or_ref=content,
                            summary=f"Content of {target_file}",
                            relevance_score=1.0,
                            freshness_score=1.0,
                            authority_level=int(AuthorityLayer.L2_REPOSITORY),
                            provenance=prov,
                            token_estimate=max(1, len(content) // 4),
                            hash=file_hash,
                        )
                    )
                except OSError:
                    continue

        return items


class GitContextProvider:
    """Provides git status and diff evidence as context."""

    def __init__(self, git_adapter: GitAdapter | None = None) -> None:
        self._git = git_adapter

    @property
    def name(self) -> str:
        return "git_provider"

    @property
    def source_type(self) -> ContextSource:
        return ContextSource.GIT

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        items: list[ContextItem] = []
        if query.workspace_scope is None:
            return items

        now = datetime.now(UTC)
        try:
            adapter = self._git or GitAdapter(Path(query.workspace_scope.root))
            status = adapter.get_status()
            if status.has_uncommitted_changes:
                summary = (
                    f"Staged: {len(status.staged_files)}, Modified: {len(status.modified_files)}"
                )
                prov = Provenance(
                    source_type=ContextSource.GIT,
                    source_id="git:status",
                    captured_at=now,
                    trust_class="current_evidence",
                    freshness=1.0,
                )
                items.append(
                    ContextItem(
                        source_type=ContextSource.GIT,
                        source_id="git:status",
                        content_or_ref={
                            "staged": status.staged_files,
                            "modified": status.modified_files,
                            "untracked": status.untracked_files,
                        },
                        summary=summary,
                        relevance_score=0.85,
                        freshness_score=1.0,
                        authority_level=int(AuthorityLayer.L3_GIT_STATE),
                        provenance=prov,
                        token_estimate=50,
                    )
                )

                # For review, validation, recovery, completion, include git diff
                if query.stage in {
                    ContextStage.REVIEW,
                    ContextStage.VALIDATION,
                    ContextStage.RECOVERY,
                    ContextStage.COMPLETION,
                }:
                    diff = adapter.get_diff()
                    if diff.strip():
                        diff_hash = hashlib.sha256(diff.encode("utf-8")).hexdigest()
                        diff_prov = Provenance(
                            source_type=ContextSource.GIT,
                            source_id="git:diff",
                            source_version=diff_hash[:16],
                            captured_at=now,
                            trust_class="current_evidence",
                            freshness=1.0,
                        )
                        items.append(
                            ContextItem(
                                source_type=ContextSource.GIT,
                                source_id="git:diff",
                                content_or_ref=diff,
                                summary="Current working tree diff",
                                relevance_score=0.95,
                                freshness_score=1.0,
                                authority_level=int(AuthorityLayer.L3_GIT_STATE),
                                provenance=diff_prov,
                                token_estimate=max(1, len(diff) // 4),
                                hash=diff_hash,
                            )
                        )
        except Exception:
            # Git unavailable or non-repo
            pass

        return items


class ValidationContextProvider:
    """Provides recent validation and error outcomes."""

    def __init__(self, validation_records: list[dict[str, Any]] | None = None) -> None:
        self._records = validation_records or []

    @property
    def name(self) -> str:
        return "validation_provider"

    @property
    def source_type(self) -> ContextSource:
        return ContextSource.VALIDATION

    def add_record(self, record: dict[str, Any]) -> None:
        self._records.append(record)

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        items: list[ContextItem] = []
        now = datetime.now(UTC)

        for i, rec in enumerate(self._records):
            prov = Provenance(
                source_type=ContextSource.VALIDATION,
                source_id=f"validation:{i}",
                captured_at=now,
                trust_class="current_evidence",
                freshness=1.0,
            )
            # High relevance during recovery and validation stages
            rel = (
                1.0
                if query.stage in {ContextStage.RECOVERY, ContextStage.VALIDATION}
                else 0.6
            )
            items.append(
                ContextItem(
                    source_type=ContextSource.VALIDATION,
                    source_id=f"validation:{i}",
                    content_or_ref=rec,
                    summary=rec.get("summary", "Validation outcome"),
                    relevance_score=rel,
                    freshness_score=1.0,
                    authority_level=int(AuthorityLayer.L4_VALIDATION),
                    provenance=prov,
                    token_estimate=max(1, len(str(rec)) // 4),
                )
            )
        return items


class MemoryContextProvider:
    """Provides active project and task memories as advisory context."""

    def __init__(
        self,
        memory_manager: ScopedMemoryManager,
        project_id: UUID | None = None,
    ) -> None:
        self._manager = memory_manager
        self._project_id = project_id

    @property
    def name(self) -> str:
        return "memory_provider"

    @property
    def source_type(self) -> ContextSource:
        return ContextSource.PROJECT_MEMORY

    def provide_context(self, query: ContextQuery) -> list[ContextItem]:
        memories = self._manager.get_scoped_memories(
            project_id=self._project_id,
            task_id=query.task_id,
            include_stale=False,
        )
        items: list[ContextItem] = []
        for mem in memories:
            src_type = (
                ContextSource.PROJECT_MEMORY
                if mem.type.value in {"PROJECT_MEMORY", "DECISION_MEMORY"}
                else ContextSource.TASK_MEMORY
            )
            auth = (
                AuthorityLayer.L5_PROJECT_MEMORY
                if src_type == ContextSource.PROJECT_MEMORY
                else AuthorityLayer.L6_TASK_MEMORY
            )
            val_content: str | dict[str, Any] = (
                mem.value if isinstance(mem.value, (dict, str)) else str(mem.value)
            )
            val_str = str(mem.value)
            items.append(
                ContextItem(
                    source_type=src_type,
                    source_id=f"mem:{mem.memory_id}",
                    content_or_ref=val_content,
                    summary=mem.summary or f"Memory: {mem.key}",
                    relevance_score=0.7,
                    freshness_score=1.0,
                    authority_level=int(auth),
                    provenance=mem.provenance,
                    sensitivity=mem.sensitivity,
                    token_estimate=max(1, len(val_str) // 4),
                )
            )
        return items

