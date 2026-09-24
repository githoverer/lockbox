from datetime import datetime, time

from src.lockbox.enforcer import LockboxEnforcer
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


def test_enforcer_checks_frequently_when_blocked():

    enforcer = LockboxEnforcer(
        [create_policy()],
        check_interval=1.0,
    )

    current_time = datetime(
        2026,
        9,
        21,
        18,
        0,
    )

    sleep_time = enforcer.get_sleep_time(
        current_time,
    )

    assert sleep_time == 1.0


def test_enforcer_sleeps_until_transition_when_allowed():

    enforcer = LockboxEnforcer(
        [create_policy()],
        check_interval=1.0,
    )

    current_time = datetime(
        2026,
        9,
        21,
        22,
        0,
    )

    sleep_time = enforcer.get_sleep_time(
        current_time,
    )

    assert sleep_time == 3600.0