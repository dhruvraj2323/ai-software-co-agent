"""Model Gateway managing replaceable provider adapters (T066)."""

from __future__ import annotations

from typing import Any

from coagent.models.adapter import MockModelAdapter, ModelAdapter
from coagent.models.contracts import (
    ModelMessage,
    ModelResponse,
    ModelUsage,
)


class ModelGateway:
    """Central gateway routing model generation to replaceable adapters."""

    def __init__(
        self,
        default_adapter: ModelAdapter | None = None,
    ) -> None:
        self._adapters: dict[str, ModelAdapter] = {}
        self._default_name: str = "default"
        self._total_usage = ModelUsage()
        self._call_count = 0

        default = default_adapter or MockModelAdapter()
        self.register_adapter(default.name, default, is_default=True)

    @property
    def total_usage(self) -> ModelUsage:
        """Total tokens accumulated across all model calls."""
        return self._total_usage

    @property
    def call_count(self) -> int:
        """Total number of generations executed."""
        return self._call_count

    def register_adapter(
        self,
        name: str,
        adapter: ModelAdapter,
        is_default: bool = False,
    ) -> None:
        """Register a named model adapter."""
        self._adapters[name] = adapter
        if is_default or len(self._adapters) == 1:
            self._default_name = name

    def get_adapter(self, name: str | None = None) -> ModelAdapter:
        """Retrieve an adapter by name or the configured default."""
        target_name = name or self._default_name
        if target_name not in self._adapters:
            raise KeyError(f"No model adapter registered with name: '{target_name}'")
        return self._adapters[target_name]

    def generate(
        self,
        messages: list[ModelMessage],
        tools: list[dict[str, Any]] | None = None,
        model_name: str | None = None,
        temperature: float = 0.2,
    ) -> ModelResponse:
        """Dispatch a generation request to the selected adapter."""
        adapter = self.get_adapter(model_name)
        response = adapter.generate(messages, tools=tools, temperature=temperature)

        self._call_count += 1
        self._total_usage = ModelUsage(
            prompt_tokens=self._total_usage.prompt_tokens + response.usage.prompt_tokens,
            completion_tokens=(
                self._total_usage.completion_tokens + response.usage.completion_tokens
            ),
            total_tokens=self._total_usage.total_tokens + response.usage.total_tokens,
        )

        return response
