"""Unit tests for context engine, ranking, budgeting, and manifests."""

from __future__ import annotations

from uuid import uuid4

from coagent.context.budget import ContextBudget, OmissionReason
from coagent.context.contracts import (
    AuthorityLayer,
    ContextItem,
    ContextQuery,
    ContextSource,
    ContextStage,
    Provenance,
)
from coagent.context.engine import ContextEngine
from coagent.context.providers import ContextProvider, TaskContextProvider
from coagent.context.ranking import ContextRanker


def test_context_ranker_stage_weighting() -> None:
    ranker = ContextRanker()

    task_item = ContextItem(
        source_type=ContextSource.TASK,
        source_id="task:1",
        content_or_ref="requirement",
        relevance_score=0.8,
        authority_level=int(AuthorityLayer.L1_TASK),
        provenance=Provenance(source_type=ContextSource.TASK, source_id="task:1"),
    )

    validation_item = ContextItem(
        source_type=ContextSource.VALIDATION,
        source_id="val:1",
        content_or_ref="test failure stack trace",
        relevance_score=0.8,
        authority_level=int(AuthorityLayer.L4_VALIDATION),
        provenance=Provenance(source_type=ContextSource.VALIDATION, source_id="val:1"),
    )

    # In PLANNING stage, task_item should outrank validation_item
    planning_ranked = ranker.filter_and_rank(
        [validation_item, task_item],
        stage=ContextStage.PLANNING,
    )
    assert planning_ranked[0][0].source_type == ContextSource.TASK

    # In RECOVERY stage, validation_item should outrank task_item due to stage multiplier
    recovery_ranked = ranker.filter_and_rank(
        [validation_item, task_item],
        stage=ContextStage.RECOVERY,
    )
    assert recovery_ranked[0][0].source_type == ContextSource.VALIDATION


def test_context_budget_manager() -> None:
    # Set tight budget
    budget = ContextBudget(
        max_total_tokens=100,
        max_total_items=2,
    )

    task_provider = TaskContextProvider({
        "requirement": "A" * 160,  # ~40 tokens
        "plan": "B" * 160,         # ~40 tokens
    })

    class ExtraProvider(ContextProvider):
        @property
        def name(self) -> str:
            return "extra"

        @property
        def source_type(self) -> ContextSource:
            return ContextSource.REPOSITORY

        def provide_context(self, query: ContextQuery) -> list[ContextItem]:
            return [
                ContextItem(
                    source_type=ContextSource.REPOSITORY,
                    source_id="repo:extra",
                    content_or_ref="C" * 200,  # ~50 tokens
                    relevance_score=0.5,
                    provenance=Provenance(
                        source_type=ContextSource.REPOSITORY,
                        source_id="repo:extra",
                    ),
                    token_estimate=50,
                )
            ]

    engine = ContextEngine(
        providers=[task_provider, ExtraProvider()],
        budget=budget,
    )

    query = ContextQuery(
        task_id=uuid4(),
        stage=ContextStage.PLANNING,
    )

    pkg = engine.assemble_context(query)
    assert len(pkg.items) == 2
    assert len(pkg.manifest.selected_items) == 2
    assert len(pkg.manifest.omitted_items) >= 1

    omitted = pkg.manifest.omitted_items[0]
    assert omitted.reason in {
        OmissionReason.MAX_ITEMS_EXCEEDED.value,
        OmissionReason.TOTAL_TOKEN_BUDGET_EXCEEDED.value,
    }


def test_context_engine_redacts_secrets() -> None:
    secret_val = "ghp_" + "1234567890abcdefghijklmnopqrstuv"

    class SecretProvider(ContextProvider):
        @property
        def name(self) -> str:
            return "secret_provider"

        @property
        def source_type(self) -> ContextSource:
            return ContextSource.TASK

        def provide_context(self, query: ContextQuery) -> list[ContextItem]:
            return [
                ContextItem(
                    source_type=ContextSource.TASK,
                    source_id="task:secret",
                    content_or_ref=f"Use token {secret_val} to connect.",
                    relevance_score=0.9,
                    provenance=Provenance(source_type=ContextSource.TASK, source_id="task:secret"),
                    token_estimate=20,
                )
            ]

    engine = ContextEngine(providers=[SecretProvider()])
    query = ContextQuery(task_id=uuid4(), stage=ContextStage.PLANNING)

    pkg = engine.assemble_context(query)
    assert secret_val not in pkg.formatted_prompt
    assert len(pkg.manifest.redactions) == 1
    assert pkg.manifest.redactions[0].redaction_type == "SECRET_MASKING"
