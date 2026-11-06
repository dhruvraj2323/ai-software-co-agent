"""MCP Policy Boundary Security Test Suite.

Verifies ST-MCP-001, ADM-012, TPS-A08 according to:
- docs/specifications/10 AI_Software_CoAgent_Security_Sandbox_Specification_v1.0_FINAL_LOCKED.md
- docs/specifications/06 AI_Software_CoAgent_Tool_Permission_Specification_v1.0_FINAL_LOCKED.md
- docs/specifications/09 AI_Software_CoAgent_Testing_Validation_Specification_v1.0_FINAL_LOCKED.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from coagent.policy.evaluator import PolicyEvaluator
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ToolRequest,
    ToolRequestSource,
)
from coagent.tools.gateway import ToolGateway
from coagent.tools.mcp import (
    McpAdapter,
    McpServerConfig,
    McpToolDefinition,
)
from coagent.tools.registry import (
    ToolCapability,
    ToolOrigin,
    ToolRegistry,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)


@pytest.fixture
def mcp_setup() -> tuple[McpAdapter, ToolRegistry, ToolGateway]:
    adapter = McpAdapter()
    adapter.register_server(
        McpServerConfig(
            server_id="database_server",
            name="External Database Server",
        )
    )

    def db_handler(args: dict[str, Any]) -> dict[str, Any]:
        return {"rows_affected": 1, "query": args.get("query")}

    mcp_tool = McpToolDefinition(
        server_id="database_server",
        name="execute_sql",
        description="Run SQL against external database",
        capability=ToolCapability.MCP_INVOKE,
        risk_level=ToolRiskLevel.HIGH,
        side_effect=ToolSideEffect.EXTERNAL,
        scope=ToolScope.NETWORK,
    )
    tool_def = adapter.register_tool(mcp_tool, handler=db_handler)

    registry = ToolRegistry()
    registry.register(tool_def)

    evaluator = PolicyEvaluator()
    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: adapter,
        policy_evaluator=evaluator,
    )
    return adapter, registry, gateway


# ST-MCP-001 (1): MCP tools must have ToolOrigin.MCP
def test_mcp_tool_origin_is_mcp(mcp_setup: tuple[McpAdapter, ToolRegistry, ToolGateway]) -> None:
    _, registry, _ = mcp_setup
    tool_def = registry.require("mcp.database_server.execute_sql")
    assert tool_def.origin == ToolOrigin.MCP
    assert tool_def.executor == "mcp.database_server"


# ST-MCP-001 (2): Invocations route through Tool Gateway and Policy Evaluator
def test_mcp_invocations_route_through_policy(
    mcp_setup: tuple[McpAdapter, ToolRegistry, ToolGateway],
) -> None:
    _, _, gateway = mcp_setup

    # In RESTRICTED mode, high-risk MCP tool cannot run
    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="mcp.database_server.execute_sql",
        tool_version="1.0",
        arguments={"query": "DROP TABLE users;"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/test"),
        autonomy_mode=AutonomyMode.RESTRICTED,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    with pytest.raises(ValueError, match="tool request (requires approval|denied by policy)"):
        gateway.route(req)


# ST-MCP-001 (3): Disabled MCP tool cannot be invoked
def test_mcp_disabled_tool_blocked(mcp_setup: tuple[McpAdapter, ToolRegistry, ToolGateway]) -> None:
    _, registry, gateway = mcp_setup
    tool_def = registry.require("mcp.database_server.execute_sql")
    tool_def.enabled = False

    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="mcp.database_server.execute_sql",
        tool_version="1.0",
        arguments={"query": "SELECT 1;"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/test"),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    with pytest.raises(ValueError, match="tool is disabled"):
        gateway.route(req)


# ST-MCP-001 (4): Version mismatch on MCP tool request is rejected
def test_mcp_version_mismatch_rejected(
    mcp_setup: tuple[McpAdapter, ToolRegistry, ToolGateway],
) -> None:
    _, _, gateway = mcp_setup

    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="mcp.database_server.execute_sql",
        tool_version="99.0",  # Mismatch with registered 1.0
        arguments={"query": "SELECT 1;"},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/test"),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    with pytest.raises(ValueError, match="tool version mismatch"):
        gateway.route(req)


# ST-MCP-001 (5): Audit hook captures MCP server and tool identity
def test_mcp_audit_hook_captures_identity() -> None:
    adapter = McpAdapter()
    adapter.register_server(McpServerConfig(server_id="metrics_server", name="Metrics"))
    tool_def = adapter.register_tool(
        McpToolDefinition(
            server_id="metrics_server",
            name="log_event",
            description="Log metric event",
            capability=ToolCapability.MCP_INVOKE,
            risk_level=ToolRiskLevel.LOW,
            side_effect=ToolSideEffect.READ,
            scope=ToolScope.NETWORK,
        ),
        handler=lambda args: {"logged": True},
    )

    registry = ToolRegistry()
    registry.register(tool_def)

    audited_decisions: list[dict[str, Any]] = []

    def mock_audit(decision: Any, request: Any, definition: Any) -> None:
        audited_decisions.append({
            "tool_id": definition.tool_id,
            "origin": definition.origin,
            "request_id": request.request_id,
        })

    gateway = ToolGateway(
        registry=registry,
        executor_resolver=lambda _: adapter,
        policy_evaluator=PolicyEvaluator(),
        audit_hook=mock_audit,
    )

    req = ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="mcp.metrics_server.log_event",
        tool_version="1.0",
        arguments={"metric": "cpu", "value": 42},
        requested_scope=Scope(workspace_id=uuid4(), root="C:/test"),
        autonomy_mode=AutonomyMode.SUPERVISED_AUTO,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )
    result = gateway.route(req)
    assert result.success
    assert len(audited_decisions) == 1
    assert audited_decisions[0]["origin"] == ToolOrigin.MCP
    assert audited_decisions[0]["tool_id"] == "mcp.metrics_server.log_event"
