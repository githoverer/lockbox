from datetime import datetime

from .policy import ApplicationPolicy
from .scheduler import is_application_allowed


def get_application_status(
    policy: ApplicationPolicy,
    current_datetime: datetime | None = None,
) -> str:
    if current_datetime is None:
        current_datetime = datetime.now()

    if is_application_allowed(policy, current_datetime):
        return "ALLOWED"

    return "BLOCKED"