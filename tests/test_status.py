from datetime import datetime, time

from src.lockbox.policy import ApplicationPolicy, TimeWindow
from src.lockbox.status import get_application_status


def test_application_status():

    policy = ApplicationPolicy(
        name="Test App",
        executable="test.exe",
        allowed_windows={
            "monday": [
                TimeWindow(
                    start=time(21, 0),
                    end=time(0, 0),
                )
            ]
        },
    )

    allowed_time = datetime(2026, 9, 21, 22, 0)
    blocked_time = datetime(2026, 9, 21, 18, 0)

    assert get_application_status(
        policy,
        allowed_time,
    ) == "ALLOWED"

    assert get_application_status(
        policy,
        blocked_time,
    ) == "BLOCKED"