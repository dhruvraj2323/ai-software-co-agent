"""Unit tests for the canonical tool registry."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from coagent.tools.registry import (
    ToolCapability,
    ToolDefinition,
    ToolOrigin,
    ToolRegistry,
    ToolRiskLevel,
    ToolScope,
    ToolSideEffect,
)


def make_definition(
    *,
    tool_id: str = "workspace.read",
    version: str = "1.0",
    enabled: bool = True,
    executor: str = "workspace",
) -> ToolDefinition:
    """Create a valid tool definition for registry tests."""
    return ToolDefinition(
        tool_id=tool_id,
        name="Workspace Read",
        description="Read files within the authorized workspace.",
        version=version,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "content": {"type": "string"},
            },
        },
        capability=ToolCapability.WORKSPACE_READ,
        risk_level=ToolRiskLevel.LOW,
        side_effects=[ToolSideEffect.READ],
        resource_scope=ToolScope.WORKSPACE,
        approval_profile="default-read",
        executor=executor,
        origin=ToolOrigin.BUILTIN,
        enabled=enabled,
    )


def test_tool_definition_validates() -> None:
    definition = make_definition()
    assert definition.tool_id == "workspace.read"
    assert definition.version == "1.0"
    assert definition.capability is ToolCapability.WORKSPACE_READ
    assert definition.risk_level is ToolRiskLevel.LOW
    assert definition.origin is ToolOrigin.BUILTIN
    assert definition.enabled is True


def test_tool_definition_rejects_empty_required_strings() -> None:
    with pytest.raises(ValidationError):
        make_definition(tool_id="")
    with pytest.raises(ValidationError):
        make_definition(version="")


def test_tool_definition_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ToolDefinition(
            **make_definition().model_dump(),
            unexpected="value",  # type: ignore[call-arg]
        )


@pytest.mark.parametrize("capability", list(ToolCapability))
def test_all_capabilities_validate(capability: ToolCapability) -> None:
    definition = make_definition()
    definition = definition.model_copy(update={"capability": capability})
    assert definition.capability is capability


@pytest.mark.parametrize("risk_level", list(ToolRiskLevel))
def test_all_risk_levels_validate(risk_level: ToolRiskLevel) -> None:
    definition = make_definition()
    definition = definition.model_copy(update={"risk_level": risk_level})
    assert definition.risk_level is risk_level


@pytest.mark.parametrize("side_effect", list(ToolSideEffect))
def test_all_side_effects_validate(side_effect: ToolSideEffect) -> None:
    definition = make_definition(
        tool_id=f"tool.{side_effect.value.lower()}",
    )
    definition = definition.model_copy(update={"side_effects": [side_effect]})
    assert definition.side_effects == [side_effect]


@pytest.mark.parametrize("scope", list(ToolScope))
def test_all_scopes_validate(scope: ToolScope) -> None:
    definition = make_definition()
    definition = definition.model_copy(update={"resource_scope": scope})
    assert definition.resource_scope is scope


@pytest.mark.parametrize("origin", list(ToolOrigin))
def test_all_origins_validate(origin: ToolOrigin) -> None:
    definition = make_definition()
    definition = definition.model_copy(update={"origin": origin})
    assert definition.origin is origin


def test_tool_definition_json_roundtrip() -> None:
    definition = make_definition()
    restored = ToolDefinition.model_validate_json(definition.model_dump_json())
    assert restored == definition


def test_registry_starts_empty() -> None:
    registry = ToolRegistry()
    assert registry.list() == ()
    assert registry.is_registered("workspace.read") is False
    assert registry.get("workspace.read") is None


def test_registry_registers_definition() -> None:
    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition)
    assert registry.is_registered("workspace.read") is True
    assert registry.get("workspace.read") == definition
    assert registry.require("workspace.read") == definition


def test_registry_rejects_duplicate_tool_id() -> None:
    registry = ToolRegistry()
    registry.register(make_definition())
    with pytest.raises(
        ValueError,
        match="tool already registered: workspace.read",
    ):
        registry.register(
            make_definition(
                version="2.0",
            )
        )


def test_registry_rejects_unknown_tool() -> None:
    registry = ToolRegistry()
    with pytest.raises(
        KeyError,
        match="unknown tool: workspace.read",
    ):
        registry.require("workspace.read")


def test_registry_preserves_disabled_definition() -> None:
    registry = ToolRegistry()
    definition = make_definition(enabled=False)
    registry.register(definition)
    registered = registry.require("workspace.read")
    assert registered.enabled is False
    assert registry.is_registered("workspace.read") is True


def test_registry_lists_definitions_in_registration_order() -> None:
    registry = ToolRegistry()
    first = make_definition(tool_id="workspace.read")
    second = make_definition(tool_id="workspace.write")
    registry.register(first)
    registry.register(second)
    assert registry.list() == (first, second)


def test_registry_does_not_execute_tools() -> None:
    registry = ToolRegistry()
    definition = make_definition(executor="workspace")
    registry.register(definition)
    registered = registry.require(definition.tool_id)
    assert registered.executor == "workspace"
    assert not callable(registered.executor)
