"""Context assembly pipeline and engine (MCS-001 §12)."""

from __future__ import annotations

from dataclasses import dataclass

from coagent.context.budget import BudgetManager, ContextBudget
from coagent.context.contracts import ContextItem, ContextQuery
from coagent.context.manifest import (
    ContextManifest,
    OmittedItemRecord,
    RedactionRecord,
    SelectedItemRecord,
)
from coagent.context.providers import ContextProvider
from coagent.context.ranking import ContextRanker
from coagent.security.secrets import contains_secret, redact_secrets


@dataclass(frozen=True)
class ContextPackage:
    """Assembled, budgeted, redacted context ready for model delivery."""

    manifest: ContextManifest
    items: list[ContextItem]
    formatted_prompt: str


class ContextEngine:
    """Orchestrates context query, ranking, budgeting, redaction, and manifest creation."""

    def __init__(
        self,
        providers: list[ContextProvider] | None = None,
        ranker: ContextRanker | None = None,
        budget: ContextBudget | None = None,
    ) -> None:
        self._providers: list[ContextProvider] = providers or []
        self._ranker = ranker or ContextRanker()
        self._default_budget = budget or ContextBudget()

    def register_provider(self, provider: ContextProvider) -> None:
        """Register a context provider."""
        self._providers.append(provider)

    def assemble_context(
        self,
        query: ContextQuery,
        budget: ContextBudget | None = None,
    ) -> ContextPackage:
        """Execute full context assembly pipeline."""
        active_budget = budget or self._default_budget

        # 1. Collect candidate items from all providers
        raw_items: list[ContextItem] = []
        for provider in self._providers:
            try:
                items = provider.provide_context(query)
                raw_items.extend(items)
            except Exception:
                # Provider failure does not crash whole assembly (MCS-001 §26)
                continue

        # 2. Filter and rank deterministically
        ranked_scored = self._ranker.filter_and_rank(raw_items, stage=query.stage)

        # 3. Enforce budget limits
        budget_mgr = BudgetManager(active_budget)
        budget_result = budget_mgr.enforce_budget(ranked_scored)

        # 4. Redact sensitive values and construct manifest records
        selected_records: list[SelectedItemRecord] = []
        redactions: list[RedactionRecord] = []
        final_items: list[ContextItem] = []

        for item, composite_score in budget_result.selected_items:
            content = item.content_or_ref

            # Redact secrets if found in text/dict
            if contains_secret(content):
                redacted_content = redact_secrets(content)
                redactions.append(
                    RedactionRecord(
                        context_id=item.context_id,
                        redaction_type="SECRET_MASKING",
                        reason=f"Secret material detected in {item.source_id}",
                    )
                )
                safe_item = item.model_copy(update={"content_or_ref": redacted_content})
            else:
                safe_item = item

            final_items.append(safe_item)
            selected_records.append(
                SelectedItemRecord(
                    context_id=safe_item.context_id,
                    source_id=safe_item.source_id,
                    source_version=safe_item.provenance.source_version,
                    relevance=safe_item.relevance_score,
                    freshness=safe_item.freshness_score,
                    token_estimate=safe_item.token_estimate,
                    composite_score=composite_score,
                )
            )

        omitted_records = [
            OmittedItemRecord(
                context_id=om.get("context_id"),
                source_id=str(om.get("source_id", "")),
                source_type=str(om.get("source_type", "")),
                reason=str(om.get("reason", "")),
                token_estimate=int(om.get("token_estimate", 0)),
            )
            for om in budget_result.omitted_items
        ]

        manifest = ContextManifest(
            task_id=query.task_id,
            stage=query.stage.value,
            context_budget=active_budget.max_total_tokens,
            total_tokens=budget_result.total_tokens,
            selected_items=selected_records,
            omitted_items=omitted_records,
            redactions=redactions,
        )

        formatted_text = self._format_package(final_items)

        return ContextPackage(
            manifest=manifest,
            items=final_items,
            formatted_prompt=formatted_text,
        )

    def _format_package(self, items: list[ContextItem]) -> str:
        sections: list[str] = []
        for item in items:
            header = (
                f"=== CONTEXT: {item.source_type.value} [{item.source_id}] "
                f"(Authority: {item.authority_level}) ==="
            )
            if isinstance(item.content_or_ref, dict):
                body = str(item.content_or_ref)
            else:
                body = str(item.content_or_ref)
            sections.append(f"{header}\n{body}\n")
        return "\n".join(sections)
