"""Model adapter protocol and test implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from coagent.models.contracts import (
    ModelMessage,
    ModelResponse,
    ModelUsage,
)


class ModelAdapter(Protocol):
    """Protocol for provider-specific model adapters."""

    @property
    def name(self) -> str:
        """Provider or adapter name."""
        ...

    def generate(
        self,
        messages: list[ModelMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> ModelResponse:
        """Generate a response from the model provider."""
        ...


class MockModelAdapter:
    """Configurable mock adapter for deterministic unit and integration tests."""

    def __init__(
        self,
        name: str = "mock-model",
        responses: list[ModelResponse] | None = None,
        generator: Callable[[list[ModelMessage]], ModelResponse] | None = None,
    ) -> None:
        self._name = name
        self._queue: list[ModelResponse] = list(responses or [])
        self._generator = generator
        self.call_history: list[list[ModelMessage]] = []

    @property
    def name(self) -> str:
        return self._name

    def queue_response(self, response: ModelResponse) -> None:
        """Queue a scripted response."""
        self._queue.append(response)

    def generate(
        self,
        messages: list[ModelMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
    ) -> ModelResponse:
        self.call_history.append(messages)

        if self._queue:
            return self._queue.pop(0)

        if self._generator is not None:
            return self._generator(messages)

        # Default fallback response
        prompt_len = sum(len(m.content) for m in messages)
        usage = ModelUsage(
            prompt_tokens=max(1, prompt_len // 4),
            completion_tokens=10,
            total_tokens=max(1, prompt_len // 4) + 10,
        )
        return ModelResponse(
            content="Mock model default response.",
            tool_calls=[],
            usage=usage,
            model_name=self._name,
            finish_reason="stop",
        )
