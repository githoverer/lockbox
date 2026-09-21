from datetime import datetime, time

from src.lockbox.policy import ApplicationPolicy, TimeWindow
from src.lockbox.scheduler import (
    is_application_allowed,
    is_time_in_window,
)


def test_normal_window():

    window = TimeWindow(
        start=time(9, 0),
        end=time(17, 0),
    )

    assert is_time_in_window(time(12, 0), window)
    assert not is_time_in_window(time(18, 0), window)


def test_overnight_window():

    window = TimeWindow(
        start=time(21, 0),
        end=time(0, 0),
    )

    assert is_time_in_window(time(21, 30), window)
    assert is_time_in_window(time(23, 59), window)

    assert not is_time_in_window(time(0, 0), window)
    assert not is_time_in_window(time(12, 0), window)


def test_application_schedule():

    policy = ApplicationPolicy(
        name="VALORANT",
        executable="VALORANT-Win64-Shipping.exe",
        allowed_windows={
            "sunday": [
                TimeWindow(
                    start=time(21, 0),
                    end=time(0, 0),
                )
            ]
        },
    )

    allowed = datetime(2026, 9, 20, 22, 0)
    blocked = datetime(2026, 9, 20, 18, 0)

    assert is_application_allowed(policy, allowed)
    assert not is_application_allowed(policy, blocked)


def test_overnight_window_continues_into_next_day():

    policy = ApplicationPolicy(
        name="Test App",
        executable="test.exe",
        allowed_windows={
            "monday": [
                TimeWindow(
                    start=time(21, 0),
                    end=time(2, 0),
                )
            ]
        },
    )

    monday_23_00 = datetime(
        2026, 9, 21, 23, 0
    )

    tuesday_01_00 = datetime(
        2026, 9, 22, 1, 0
    )

    tuesday_02_00 = datetime(
        2026, 9, 22, 2, 0
    )

    tuesday_03_00 = datetime(
        2026, 9, 22, 3, 0
    )

    assert is_application_allowed(
        policy,
        monday_23_00,
    )

    assert is_application_allowed(
        policy,
        tuesday_01_00,
    )

    assert not is_application_allowed(
        policy,
        tuesday_02_00,
    )

    assert not is_application_allowed(
        policy,
        tuesday_03_00,
    )