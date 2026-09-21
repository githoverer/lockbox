from datetime import datetime, time

from src.lockbox.enforcement import get_enforcement_action
from src.lockbox.policy import ApplicationPolicy, TimeWindow


def create_policy():
    return ApplicationPolicy(
        name="Test App",
        executable="test.exe",
        allowed_windows={
            "monday": [
                TimeWindow(
                    start=time(21, 0),
                    end=time(23, 0),
                )
            ]
        },
    )


def test_blocked_running_application_requires_termination():

    policy = create_policy()

    blocked_time = datetime(
        2026, 9, 21, 18, 0
    )

    action = get_enforcement_action(
        policy,
        blocked_time,
        process_checker=lambda _: True,
    )

    assert action == "TERMINATE"


def test_allowed_running_application_requires_no_action():

    policy = create_policy()

    allowed_time = datetime(
        2026, 9, 21, 22, 0
    )

    action = get_enforcement_action(
        policy,
        allowed_time,
        process_checker=lambda _: True,
    )

    assert action == "NO_ACTION"


def test_blocked_application_that_is_not_running_requires_no_action():

    policy = create_policy()

    blocked_time = datetime(
        2026, 9, 21, 18, 0
    )

    action = get_enforcement_action(
        policy,
        blocked_time,
        process_checker=lambda _: False,
    )

    assert action == "NO_ACTION"