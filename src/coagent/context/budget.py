"""Deterministic context budgeting and token allocation (MCS-001 §11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField

from coagent.context.contracts import ContextItem, ContextSource


class OmissionReason(StrEnum):
    """Reason why an item was excluded or truncated by the budget manager."""

    TOTAL_TOKEN_BUDGET_EXCEEDED = "TOTAL_TOKEN_BUDGET_EXCEEDED"
    PROVIDER_BUDGET_EXCEEDED = "PROVIDER_BUDGET_EXCEEDED"
    MAX_ITEMS_EXCEEDED = "MAX_ITEMS_EXCEEDED"
    LOW_RELEVANCE = "LOW_RELEVANCE"


class ContextBudget(BaseModel):
    """Configured resource limits for model-facing context packages."""

    model_config = ConfigDict(extra="forbid")

    max_total_tokens: int = PydanticField(default=8000, ge=10)
    max_total_items: int = PydanticField(default=40, ge=1)
    max_item_tokens: int = PydanticField(default=1500, ge=10)
    provider_budgets: dict[ContextSource, int] = PydanticField(default_factory=dict)


@dataclass
class BudgetResult:
    """Outcome of budget enforcement over ranked items."""

    selected_items: list[tuple[ContextItem, float]]
    omitted_items: list[dict[str, Any]] = field(default_factory=list)
    total_tokens: int = 0


class BudgetManager:
    """Applies global, provider, and item-level token limits deterministically."""

    def __init__(self, budget: ContextBudget | None = None) -> None:
        self._budget = budget or ContextBudget()

    def enforce_budget(
        self,
        ranked_items: list[tuple[ContextItem, float]],
    ) -> BudgetResult:
        """Select items within budget and record explainable omissions."""
        selected: list[tuple[ContextItem, float]] = []
        omitted: list[dict[str, Any]] = []

        total_tokens = 0
        provider_tokens: dict[ContextSource, int] = {}

        for item, score in ranked_items:
            # Check maximum items limit
            if len(selected) >= self._budget.max_total_items:
                omitted.append({
                    "context_id": item.context_id,
                    "source_id": item.source_id,
                    "source_type": item.source_type,
                    "reason": OmissionReason.MAX_ITEMS_EXCEEDED.value,
                    "token_estimate": item.token_estimate,
                })
                continue

            # Estimate and enforce item-level limit by truncation if needed
            effective_item = item
            item_tokens = item.token_estimate
            if item_tokens > self._budget.max_item_tokens:
                # Truncate content
                max_chars = self._budget.max_item_tokens * 4
                if isinstance(item.content_or_ref, str):
                    truncated_content = (
                        item.content_or_ref[:max_chars] + "\n... (truncated to fit budget)"
                    )
                    effective_item = item.model_copy(
                        update={
                            "content_or_ref": truncated_content,
                            "token_estimate": self._budget.max_item_tokens,
                        }
                    )
                    item_tokens = self._budget.max_item_tokens

            # Check provider budget limit
            provider_limit = self._budget.provider_budgets.get(item.source_type)
            current_provider_tokens = provider_tokens.get(item.source_type, 0)
            if (
                provider_limit is not None
                and (current_provider_tokens + item_tokens) > provider_limit
            ):
                omitted.append({
                    "context_id": item.context_id,
                    "source_id": item.source_id,
                    "source_type": item.source_type,
                    "reason": OmissionReason.PROVIDER_BUDGET_EXCEEDED.value,
                    "token_estimate": item_tokens,
                })
                continue

            # Check total token budget
            if (total_tokens + item_tokens) > self._budget.max_total_tokens:
                omitted.append({
                    "context_id": item.context_id,
                    "source_id": item.source_id,
                    "source_type": item.source_type,
                    "reason": OmissionReason.TOTAL_TOKEN_BUDGET_EXCEEDED.value,
                    "token_estimate": item_tokens,
                })
                continue

            selected.append((effective_item, score))
            total_tokens += item_tokens
            provider_tokens[item.source_type] = current_provider_tokens + item_tokens

        return BudgetResult(
            selected_items=selected,
            omitted_items=omitted,
            total_tokens=total_tokens,
        )
