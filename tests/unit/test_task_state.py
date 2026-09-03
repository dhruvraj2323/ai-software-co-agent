"""Tests for the runtime task lifecycle state machine."""

import pytest

from coagent.runtime.task_state import (
    InvalidTaskTransitionError,
    TaskState,
    TaskStateMachine,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (TaskState.CREATED, TaskState.PLANNING),
        (TaskState.CREATED, TaskState.CANCELLED),
        (TaskState.PLANNING, TaskState.READY),
        (TaskState.PLANNING, TaskState.BLOCKED),
        (TaskState.PLANNING, TaskState.FAILED),
        (TaskState.PLANNING, TaskState.CANCELLED),
        (TaskState.READY, TaskState.IMPLEMENTING),
        (TaskState.READY, TaskState.BLOCKED),
        (TaskState.READY, TaskState.CANCELLED),
        (TaskState.IMPLEMENTING, TaskState.VALIDATING),
        (TaskState.IMPLEMENTING, TaskState.BLOCKED),
        (TaskState.IMPLEMENTING, TaskState.FAILED),
        (TaskState.IMPLEMENTING, TaskState.CANCELLED),
        (TaskState.VALIDATING, TaskState.COMPLETE),
        (TaskState.VALIDATING, TaskState.FAILED),
        (TaskState.VALIDATING, TaskState.BLOCKED),
        (TaskState.VALIDATING, TaskState.CANCELLED),
        (TaskState.RECOVERING, TaskState.VALIDATING),
        (TaskState.RECOVERING, TaskState.BLOCKED),
        (TaskState.RECOVERING, TaskState.FAILED),
        (TaskState.RECOVERING, TaskState.CANCELLED),
        (TaskState.BLOCKED, TaskState.READY),
        (TaskState.BLOCKED, TaskState.IMPLEMENTING),
        (TaskState.BLOCKED, TaskState.CANCELLED),
    ],
)
def test_allowed_transition(
    current: TaskState,
    target: TaskState,
) -> None:
    machine = TaskStateMachine(current)

    assert machine.can_transition(target)

    machine.transition(target)

    assert machine.state is target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (TaskState.CREATED, TaskState.READY),
        (TaskState.CREATED, TaskState.IMPLEMENTING),
        (TaskState.CREATED, TaskState.COMPLETE),
        (TaskState.PLANNING, TaskState.IMPLEMENTING),
        (TaskState.PLANNING, TaskState.COMPLETE),
        (TaskState.READY, TaskState.COMPLETE),
        (TaskState.READY, TaskState.VALIDATING),
        (TaskState.IMPLEMENTING, TaskState.COMPLETE),
        (TaskState.IMPLEMENTING, TaskState.READY),
        (TaskState.VALIDATING, TaskState.READY),
        (TaskState.RECOVERING, TaskState.COMPLETE),
        (TaskState.BLOCKED, TaskState.COMPLETE),
        (TaskState.COMPLETE, TaskState.CREATED),
        (TaskState.COMPLETE, TaskState.PLANNING),
        (TaskState.CANCELLED, TaskState.CREATED),
        (TaskState.CANCELLED, TaskState.PLANNING),
        (TaskState.FAILED, TaskState.PLANNING),
    ],
)
def test_invalid_transition_is_rejected(
    current: TaskState,
    target: TaskState,
) -> None:
    machine = TaskStateMachine(current)

    assert not machine.can_transition(target)

    with pytest.raises(InvalidTaskTransitionError):
        machine.transition(target)


def test_failed_to_recover_requires_explicit_recovery_permission() -> None:
    machine = TaskStateMachine(TaskState.FAILED)

    assert not machine.can_transition(
        TaskState.RECOVERING,
        recovery_available=False,
    )

    with pytest.raises(InvalidTaskTransitionError):
        machine.transition(
            TaskState.RECOVERING,
            recovery_available=False,
        )


def test_failed_state_does_not_recover_when_recovery_is_unavailable() -> None:
    machine = TaskStateMachine(TaskState.FAILED)

    with pytest.raises(InvalidTaskTransitionError):
        machine.transition(
            TaskState.RECOVERING,
            recovery_available=True,
        )


def test_validation_can_enter_recovery_when_available() -> None:
    machine = TaskStateMachine(TaskState.VALIDATING)

    assert machine.can_transition(
        TaskState.RECOVERING,
        recovery_available=True,
    )

    machine.transition(
        TaskState.RECOVERING,
        recovery_available=True,
    )

    assert machine.state is TaskState.RECOVERING


def test_failed_state_is_terminal_without_recovery_path() -> None:
    machine = TaskStateMachine(TaskState.FAILED)

    for target in TaskState:
        if target is not TaskState.RECOVERING:
            assert not machine.can_transition(target)


def test_complete_state_is_terminal() -> None:
    machine = TaskStateMachine(TaskState.COMPLETE)

    for target in TaskState:
        assert not machine.can_transition(target)


def test_cancelled_state_is_terminal() -> None:
    machine = TaskStateMachine(TaskState.CANCELLED)

    for target in TaskState:
        assert not machine.can_transition(target)


def test_default_state_is_created() -> None:
    machine = TaskStateMachine()

    assert machine.state is TaskState.CREATED
