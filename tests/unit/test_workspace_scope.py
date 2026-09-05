"""Unit tests for the canonical workspace scope contract."""
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coagent.workspace import WorkspaceScope


def test_workspace_scope_requires_explicit_task_and_workspace_identity() -> None:
    task_id = uuid4()
    workspace_id = uuid4()
    scope = WorkspaceScope(
        task_id=task_id,
        workspace_id=workspace_id,
        root="C:/Projects/example",
    )
    assert scope.task_id == task_id
    assert scope.workspace_id == workspace_id
    assert scope.root == "C:/Projects/example"
def test_workspace_scope_is_explicitly_associated_with_task() -> None:
    task_id = uuid4()
    scope = WorkspaceScope(
        task_id=task_id,
        workspace_id=uuid4(),
        root="C:/Projects/example",
    )
    assert scope.task_id == task_id
def test_workspace_scope_rejects_empty_root() -> None:
    with pytest.raises(ValidationError):
        WorkspaceScope(
            task_id=uuid4(),
            workspace_id=uuid4(),
            root="",
        )
def test_workspace_scope_rejects_missing_task_identity() -> None:
    with pytest.raises(ValidationError):
        WorkspaceScope(
            workspace_id=uuid4(),
            root="C:/Projects/example",
        )
def test_workspace_scope_rejects_missing_workspace_identity() -> None:
    with pytest.raises(ValidationError):
        WorkspaceScope(
            task_id=uuid4(),
            root="C:/Projects/example",
        )
def test_workspace_scope_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        WorkspaceScope(
            task_id=uuid4(),
            workspace_id=uuid4(),
            root="C:/Projects/example",
            unexpected="not-allowed",
        )
def test_workspace_scope_does_not_use_current_working_directory_implicitly() -> None:
    with pytest.raises(ValidationError):
        WorkspaceScope(
            task_id=uuid4(),
            workspace_id=uuid4(),
        )
