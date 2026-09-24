from datetime import datetime, time, timedelta

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

    # Overnight window: 21:00 → 02:00
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

    # Check today's windows.
    today_windows = policy.allowed_windows.get(
        current_day,
        [],
    )

    for window in today_windows:
        if is_time_in_window(current_time, window):
            return True

    # Check overnight window continuing from yesterday.
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


def get_next_transition(
    policy: ApplicationPolicy,
    current_datetime: datetime,
) -> datetime | None:

    candidates = []

    current_date = current_datetime.date()

    # Look slightly more than one week ahead so weekly
    # schedules always have a future boundary available.
    for day_offset in range(9):

        date = current_date + timedelta(
            days=day_offset
        )

        day_name = date.strftime("%A").lower()

        windows = policy.allowed_windows.get(
            day_name,
            [],
        )

        for window in windows:

            # start == end represents a 24-hour window,
            # so it has no transition.
            if window.start == window.end:
                continue

            start_datetime = datetime.combine(
                date,
                window.start,
            )

            # Normal window.
            if window.start < window.end:

                end_datetime = datetime.combine(
                    date,
                    window.end,
                )

            # Overnight window.
            else:

                end_datetime = datetime.combine(
                    date + timedelta(days=1),
                    window.end,
                )

            candidates.append(start_datetime)
            candidates.append(end_datetime)

    future_candidates = [
        candidate
        for candidate in candidates
        if candidate > current_datetime
    ]

    if not future_candidates:
        return None

    return min(future_candidates)