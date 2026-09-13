"""Unit tests for canonical tool request and result contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.core.errors import ErrorRecord
from coagent.core.types import EventSeverity, Recoverability
from coagent.tools.contracts import (
    AutonomyMode,
    Scope,
    ScopeEffect,
    ToolRequest,
    ToolRequestSource,
    ToolResult,
    ToolResultStatus,
)


def make_error() -> ErrorRecord:
    """Create a valid canonical error record for result tests."""
    now = datetime.now(UTC)
    return ErrorRecord(
        error_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        category="TOOL",
        code="TOOL_FAILED",
        source="tool",
        message="tool execution failed",
        severity=EventSeverity.ERROR,
        recoverability=Recoverability.NONE,
        occurred_at=now,
        normalized_at=now,
    )


def make_scope() -> Scope:
    """Create a valid workspace scope."""
    return Scope(
        workspace_id=uuid4(),
        root="C:/workspace/project",
    )


def make_request() -> ToolRequest:
    """Create a valid canonical tool request."""
    return ToolRequest(
        request_id=uuid4(),
        task_id=uuid4(),
        correlation_id=uuid4(),
        tool_id="workspace.read",
        tool_version="1.0",
        arguments={"path": "README.md"},
        requested_scope=make_scope(),
        autonomy_mode=AutonomyMode.ASSISTED_IMPLEMENT,
        source=ToolRequestSource.AGENT,
        created_at=datetime.now(UTC),
    )


def test_tool_request_validates() -> None:
    request = make_request()
    assert request.tool_id == "workspace.read"
    assert request.tool_version == "1.0"
    assert request.arguments == {"path": "README.md"}
    assert request.source is ToolRequestSource.AGENT
    assert request.autonomy_mode is AutonomyMode.ASSISTED_IMPLEMENT


def test_tool_request_preserves_correlation_ids() -> None:
    request_id = uuid4()
    task_id = uuid4()
    correlation_id = uuid4()
    request = ToolRequest(
        request_id=request_id,
        task_id=task_id,
        correlation_id=correlation_id,
        tool_id="workspace.read",
        tool_version="1.0",
        arguments={},
        requested_scope=make_scope(),
        autonomy_mode=AutonomyMode.PLAN,
        source=ToolRequestSource.USER,
        created_at=datetime.now(UTC),
    )
    assert request.request_id == request_id
    assert request.task_id == task_id
    assert request.correlation_id == correlation_id


def test_tool_request_rejects_empty_tool_id() -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id=uuid4(),
            task_id=uuid4(),
            correlation_id=uuid4(),
            tool_id="",
            tool_version="1.0",
            arguments={},
            requested_scope=make_scope(),
            autonomy_mode=AutonomyMode.PLAN,
            source=ToolRequestSource.AGENT,
            created_at=datetime.now(UTC),
        )


def test_tool_request_rejects_empty_tool_version() -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id=uuid4(),
            task_id=uuid4(),
            correlation_id=uuid4(),
            tool_id="workspace.read",
            tool_version="",
            arguments={},
            requested_scope=make_scope(),
            autonomy_mode=AutonomyMode.PLAN,
            source=ToolRequestSource.AGENT,
            created_at=datetime.now(UTC),
        )


def test_tool_request_rejects_non_object_arguments() -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id=uuid4(),
            task_id=uuid4(),
            correlation_id=uuid4(),
            tool_id="workspace.read",
            tool_version="1.0",
            arguments=["README.md"],  # type: ignore[arg-type]
            requested_scope=make_scope(),
            autonomy_mode=AutonomyMode.PLAN,
            source=ToolRequestSource.AGENT,
            created_at=datetime.now(UTC),
        )


def test_tool_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ToolRequest(
            request_id=uuid4(),
            task_id=uuid4(),
            correlation_id=uuid4(),
            tool_id="workspace.read",
            tool_version="1.0",
            arguments={},
            requested_scope=make_scope(),
            autonomy_mode=AutonomyMode.PLAN,
            source=ToolRequestSource.AGENT,
            created_at=datetime.now(UTC),
            unexpected="value",  # type: ignore[call-arg]
        )


@pytest.mark.parametrize("source", list(ToolRequestSource))
def test_all_tool_request_sources_validate(source: ToolRequestSource) -> None:
    request = make_request().model_copy(update={"source": source})
    assert request.source is source


@pytest.mark.parametrize("mode", list(AutonomyMode))
def test_all_autonomy_modes_validate(mode: AutonomyMode) -> None:
    request = make_request().model_copy(update={"autonomy_mode": mode})
    assert request.autonomy_mode is mode


def test_tool_request_json_roundtrip() -> None:
    request = make_request()
    restored = ToolRequest.model_validate_json(request.model_dump_json())
    assert restored == request


def test_scope_rejects_empty_root() -> None:
    with pytest.raises(ValidationError):
        Scope(
            workspace_id=uuid4(),
            root="",
        )


def test_scope_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Scope(
            workspace_id=uuid4(),
            root="C:/workspace/project",
            unexpected="value",  # type: ignore[call-arg]
        )


def test_successful_tool_result_validates() -> None:
    request_id = uuid4()
    result = ToolResult(
        request_id=request_id,
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"content": "hello"},
        scope_effect=ScopeEffect.UNCHANGED,
        created_at=datetime.now(UTC),
    )
    assert result.request_id == request_id
    assert result.success is True
    assert result.status is ToolResultStatus.SUCCESS
    assert result.output == {"content": "hello"}
    assert result.error is None


@pytest.mark.parametrize(
    "status",
    [
        ToolResultStatus.FAILED,
        ToolResultStatus.DENIED,
        ToolResultStatus.BLOCKED,
        ToolResultStatus.CANCELLED,
    ],
)
def test_non_success_tool_results_validate(
    status: ToolResultStatus,
) -> None:
    result = ToolResult(
        request_id=uuid4(),
        success=False,
        status=status,
        error=make_error(),
        scope_effect=ScopeEffect.NONE,
        created_at=datetime.now(UTC),
    )
    assert result.success is False
    assert result.status is status
    assert result.error is not None


def test_success_requires_success_status() -> None:
    with pytest.raises(
        ValidationError,
        match="successful tool results must have SUCCESS status",
    ):
        ToolResult(
            request_id=uuid4(),
            success=True,
            status=ToolResultStatus.BLOCKED,
            output={"content": "value"},
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )


def test_success_requires_output() -> None:
    with pytest.raises(
        ValidationError,
        match="successful tool results must contain output",
    ):
        ToolResult(
            request_id=uuid4(),
            success=True,
            status=ToolResultStatus.SUCCESS,
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )


def test_success_cannot_contain_error() -> None:
    with pytest.raises(
        ValidationError,
        match="successful tool results cannot contain an error",
    ):
        ToolResult(
            request_id=uuid4(),
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={"content": "value"},
            error=make_error(),
            scope_effect=ScopeEffect.UNCHANGED,
            created_at=datetime.now(UTC),
        )


def test_failed_result_requires_error() -> None:
    with pytest.raises(
        ValidationError,
        match="failed tool results must contain an error",
    ):
        ToolResult(
            request_id=uuid4(),
            success=False,
            status=ToolResultStatus.FAILED,
            scope_effect=ScopeEffect.NONE,
            created_at=datetime.now(UTC),
        )


def test_failed_result_cannot_have_success_status() -> None:
    with pytest.raises(
        ValidationError,
        match="failed tool results cannot have SUCCESS status",
    ):
        ToolResult(
            request_id=uuid4(),
            success=False,
            status=ToolResultStatus.SUCCESS,
            error=make_error(),
            scope_effect=ScopeEffect.NONE,
            created_at=datetime.now(UTC),
        )


def test_failed_result_cannot_contain_output() -> None:
    with pytest.raises(
        ValidationError,
        match="failed tool results cannot contain output",
    ):
        ToolResult(
            request_id=uuid4(),
            success=False,
            status=ToolResultStatus.FAILED,
            output={"unexpected": "value"},
            error=make_error(),
            scope_effect=ScopeEffect.NONE,
            created_at=datetime.now(UTC),
        )


def test_negative_duration_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ToolResult(
            request_id=uuid4(),
            success=True,
            status=ToolResultStatus.SUCCESS,
            output={},
            duration_ms=-1,
            scope_effect=ScopeEffect.NONE,
            created_at=datetime.now(UTC),
        )


def test_tool_result_json_roundtrip() -> None:
    result = ToolResult(
        request_id=uuid4(),
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={"files": ["README.md"]},
        exit_code=0,
        duration_ms=125,
        evidence_ref="evidence://tool/123",
        scope_effect=ScopeEffect.UNCHANGED,
        created_at=datetime.now(UTC),
    )
    restored = ToolResult.model_validate_json(result.model_dump_json())
    assert restored == result


@pytest.mark.parametrize("scope_effect", list(ScopeEffect))
def test_all_scope_effects_validate(scope_effect: ScopeEffect) -> None:
    result = ToolResult(
        request_id=uuid4(),
        success=True,
        status=ToolResultStatus.SUCCESS,
        output={},
        scope_effect=scope_effect,
        created_at=datetime.now(UTC),
    )
    assert result.scope_effect is scope_effect
