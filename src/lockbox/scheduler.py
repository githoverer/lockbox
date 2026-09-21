from datetime import datetime, time

from .policy import ApplicationPolicy, TimeWindow


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def is_time_in_window(
    current_time: time,
    window: TimeWindow,
) -> bool:

    # Normal window: 09:00 → 17:00
    if window.start < window.end:
        return window.start <= current_time < window.end

    # Same start/end means 24 hours.
    if window.start == window.end:
        return True

    # Overnight window: 21:00 → 00:00
    return (
        current_time >= window.start
        or current_time < window.end
    )


def is_application_allowed(
    policy: ApplicationPolicy,
    current_datetime: datetime,
) -> bool:

    current_day = current_datetime.strftime("%A").lower()
    current_time = current_datetime.time()

    # Check today's schedule.
    today_windows = policy.allowed_windows.get(
        current_day,
        [],
    )

    for window in today_windows:
        if is_time_in_window(current_time, window):
            return True

    # Check whether an overnight window from yesterday
    # continues into today.
    current_index = DAYS.index(current_day)
    previous_day = DAYS[current_index - 1]

    previous_windows = policy.allowed_windows.get(
        previous_day,
        [],
    )

    for window in previous_windows:

        if window.start > window.end:
            if current_time < window.end:
                return True

    return False