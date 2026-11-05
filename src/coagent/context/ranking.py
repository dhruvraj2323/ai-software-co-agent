"""Context ranking, stage weighting, and filtering pipeline (MCS-001 §10, §13)."""

from __future__ import annotations

from datetime import UTC, datetime

from coagent.context.contracts import (
    ContextItem,
    ContextSource,
    ContextStage,
    SensitivityClass,
)


class ContextRanker:
    """Ranks and filters context items deterministically based on authority and stage."""

    STAGE_WEIGHTS: dict[ContextStage, dict[ContextSource, float]] = {
        ContextStage.UNDERSTANDING: {
            ContextSource.TASK: 1.2,
            ContextSource.REPOSITORY: 1.0,
            ContextSource.PROJECT_MEMORY: 0.9,
            ContextSource.TASK_MEMORY: 0.8,
        },
        ContextStage.PLANNING: {
            ContextSource.TASK: 1.1,
            ContextSource.REPOSITORY: 1.3,
            ContextSource.SYMBOL: 1.1,
            ContextSource.PROJECT_MEMORY: 0.9,
        },
        ContextStage.IMPLEMENTATION: {
            ContextSource.REPOSITORY: 1.3,
            ContextSource.SYMBOL: 1.2,
            ContextSource.GIT: 1.1,
            ContextSource.TASK: 1.0,
        },
        ContextStage.REVIEW: {
            ContextSource.GIT: 1.3,
            ContextSource.TASK: 1.1,
            ContextSource.VALIDATION: 1.1,
        },
        ContextStage.VALIDATION: {
            ContextSource.VALIDATION: 1.4,
            ContextSource.GIT: 1.2,
            ContextSource.REPOSITORY: 1.0,
        },
        ContextStage.RECOVERY: {
            ContextSource.FAILURE: 1.5,
            ContextSource.VALIDATION: 1.4,
            ContextSource.GIT: 1.2,
            ContextSource.REPOSITORY: 1.1,
            ContextSource.TASK: 1.0,
            ContextSource.PROJECT_MEMORY: 0.5,
            ContextSource.TASK_MEMORY: 0.5,
        },
        ContextStage.COMPLETION: {
            ContextSource.VALIDATION: 1.4,
            ContextSource.TASK: 1.3,
            ContextSource.GIT: 1.1,
        },
        ContextStage.REPORTING: {
            ContextSource.TASK: 1.1,
            ContextSource.VALIDATION: 1.1,
            ContextSource.GIT: 1.1,
        },
    }

    def __init__(self, allow_confidential: bool = False) -> None:
        self._allow_confidential = allow_confidential

    def filter_and_rank(
        self,
        items: list[ContextItem],
        stage: ContextStage,
        min_relevance: float = 0.1,
    ) -> list[tuple[ContextItem, float]]:
        """Filter out stale/sensitive items, returning ranked items with composite scores."""
        now = datetime.now(UTC)
        stage_factors = self.STAGE_WEIGHTS.get(stage, {})

        seen_sources: set[str] = set()
        seen_hashes: set[str] = set()

        scored_items: list[tuple[ContextItem, float]] = []

        for item in items:
            # 1. Check expiration
            if item.expires_at is not None and item.expires_at <= now:
                continue

            # 2. Check sensitivity
            if item.sensitivity == SensitivityClass.RESTRICTED:
                continue
            if item.sensitivity == SensitivityClass.CONFIDENTIAL and not self._allow_confidential:
                continue

            # 3. Deduplicate
            if item.source_id in seen_sources:
                continue
            if item.hash and item.hash in seen_hashes:
                continue

            seen_sources.add(item.source_id)
            if item.hash:
                seen_hashes.add(item.hash)

            # 4. Compute composite score
            # Base authority component (0.0 to 1.0)
            authority_norm = min(1.0, max(0.0, item.authority_level / 100.0))

            stage_mult = stage_factors.get(item.source_type, 1.0)

            # Weighting: 40% authority, 40% task relevance, 20% freshness
            composite = (
                (authority_norm * 0.4)
                + (item.relevance_score * 0.4)
                + (item.freshness_score * 0.2)
            ) * stage_mult

            if item.relevance_score < min_relevance:
                continue

            scored_items.append((item, round(composite, 4)))

        # Sort descending by composite score
        scored_items.sort(key=lambda pair: pair[1], reverse=True)
        return scored_items
