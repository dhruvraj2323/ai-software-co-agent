from coagent.core.types import EventSeverity, Recoverability


def test_event_severity_values() -> None:
    assert {item.value for item in EventSeverity} == {
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }


def test_recoverability_values() -> None:
    assert {item.value for item in Recoverability} == {
        "AUTO",
        "ASSISTED",
        "MANUAL",
        "NONE",
    }
