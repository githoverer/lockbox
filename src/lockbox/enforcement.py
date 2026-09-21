from datetime import datetime
from typing import Callable

from .policy import ApplicationPolicy
from .process import is_process_running
from .scheduler import is_application_allowed


def get_enforcement_action(
    policy: ApplicationPolicy,
    current_datetime: datetime | None = None,
    process_checker: Callable[[str], bool] = is_process_running,
) -> str:

    if current_datetime is None:
        current_datetime = datetime.now()

    allowed = is_application_allowed(
        policy,
        current_datetime,
    )

    running = process_checker(
        policy.executable,
    )

    if not allowed and running:
        return "TERMINATE"

    return "NO_ACTION"