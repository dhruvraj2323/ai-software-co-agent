"""Contract tests for the canonical task lifecycle transition matrix."""

from __future__ import annotations

import pytest

from coagent.runtime.task_state import (
    InvalidTaskTransitionError,
    TaskState,
    TaskStateMachine,
)

# Independent contract definition. Do not import the implementation's private
# transition table: these expectations must detect accidental implementation
# changes rather than mirror them.
EXPECTED_TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
    TaskState.CREATED: frozenset(
        {TaskState.PLANNING, TaskState.CANCELLED}
    ),
    TaskState.PLANNING: frozenset(
        {
            TaskState.READY,
            TaskState.BLOCKED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.READY: frozenset(
        {
            TaskState.IMPLEMENTING,
            TaskState.BLOCKED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.IMPLEMENTING: frozenset(
        {
            TaskState.VALIDATING,
            TaskState.BLOCKED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.VALIDATING: frozenset(
        {
            TaskState.COMPLETE,
            TaskState.RECOVERING,
            TaskState.FAILED,
            TaskState.BLOCKED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.RECOVERING: frozenset(
        {
            TaskState.VALIDATING,
            TaskState.BLOCKED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        }
    ),
    TaskState.BLOCKED: frozenset(
        {
            TaskState.READY,
            TaskState.IMPLEMENTING,
            TaskState.CANCELLED,
        }
    ),
    TaskState.FAILED: frozenset(),
    TaskState.COMPLETE: frozenset(),
    TaskState.CANCELLED: frozenset(),
}


@pytest.mark.parametrize("current", list(TaskState))
@pytest.mark.parametrize("target", list(TaskState))
def test_can_transition_matches_complete_contract_matrix(
    current: TaskState,
    target: TaskState,
) -> None:
    """Every state/target pair must match the locked transition contract."""
    machine = TaskStateMachine(current)
    expected = target in EXPECTED_TRANSITIONS[current]

    assert (
        machine.can_transition(
            target,
            recovery_available=True,
        )
        is expected
    )


@pytest.mark.parametrize("current", list(TaskState))
@pytest.mark.parametrize("target", list(TaskState))
def test_transition_accepts_or_rejects_every_contract_pair(
    current: TaskState,
    target: TaskState,
) -> None:
    """Allowed pairs transition; every other pair is rejected."""
    machine = TaskStateMachine(current)
    expected = target in EXPECTED_TRANSITIONS[current]

    if expected:
        machine.transition(
            target,
            recovery_available=True,
        )
        assert machine.state is target
    else:
        with pytest.raises(InvalidTaskTransitionError):
            machine.transition(
                target,
                recovery_available=True,
            )

        assert machine.state is current


def test_validating_to_recovering_requires_recovery_availability() -> None:
    """Recovery is explicitly gated for VALIDATING -> RECOVERING."""
    machine = TaskStateMachine(TaskState.VALIDATING)

    assert (
        machine.can_transition(
            TaskState.RECOVERING
        )
        is False
    )

    machine.transition(
        TaskState.RECOVERING,
        recovery_available=True,
    )

    assert machine.state is TaskState.RECOVERING


def test_failed_to_recovering_remains_disallowed_even_when_recovery_is_available() -> None:
    """FAILED has no outgoing transition in the canonical contract."""
    machine = TaskStateMachine(TaskState.FAILED)

    assert (
        machine.can_transition(
            TaskState.RECOVERING,
            recovery_available=True,
        )
        is False
    )

    with pytest.raises(InvalidTaskTransitionError):
        machine.transition(
            TaskState.RECOVERING,
            recovery_available=True,
        )

    assert machine.state is TaskState.FAILED


def test_terminal_states_have_no_outgoing_transitions() -> None:
    """FAILED, COMPLETE, and CANCELLED are terminal states."""
    for current in (
        TaskState.FAILED,
        TaskState.COMPLETE,
        TaskState.CANCELLED,
    ):
        machine = TaskStateMachine(current)

        assert all(
            not machine.can_transition(
                target,
                recovery_available=True,
            )
            for target in TaskState
        )