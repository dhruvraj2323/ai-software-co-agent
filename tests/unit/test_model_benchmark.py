"""Model Gateway benchmark and latency baseline tests (T074)."""

from __future__ import annotations

import time

from coagent.models.adapter import MockModelAdapter
from coagent.models.contracts import MessageRole, ModelMessage, ModelResponse, ModelUsage
from coagent.models.gateway import ModelGateway


def test_model_gateway_benchmark() -> None:
    adapter = MockModelAdapter(name="bench-adapter")
    for i in range(100):
        adapter.queue_response(
            ModelResponse(
                content=f"Response {i}",
                usage=ModelUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
                model_name="bench-adapter",
            )
        )

    gateway = ModelGateway(default_adapter=adapter)
    msg = [ModelMessage(role=MessageRole.USER, content="Benchmark query")]

    start_t = time.perf_counter()
    for _ in range(100):
        res = gateway.generate(msg)
        assert res.model_name == "bench-adapter"
    duration = time.perf_counter() - start_t

    # 100 in-memory dispatches must complete in well under 0.5s
    assert duration < 0.5
    assert gateway.call_count == 100
    assert gateway.total_usage.prompt_tokens == 5000
    assert gateway.total_usage.completion_tokens == 2000
    assert gateway.total_usage.total_tokens == 7000
