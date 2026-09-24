import time as time_module
from datetime import datetime

from .enforcement import get_enforcement_action
from .policy import ApplicationPolicy
from .process import terminate_process
from .scheduler import (
    get_next_transition,
    is_application_allowed,
)


class LockboxEnforcer:

    def __init__(
        self,
        policies: list[ApplicationPolicy],
        check_interval: float = 1.0,
    ):
        self.policies = policies
        self.check_interval = check_interval
        self.running = False

    def enforce_once(self) -> None:

        current_time = datetime.now()

        for policy in self.policies:

            action = get_enforcement_action(
                policy,
                current_time,
            )

            if action == "TERMINATE":

                terminate_process(
                    policy.executable,
                )

    def get_sleep_time(
        self,
        current_time: datetime | None = None,
    ) -> float:

        if current_time is None:
            current_time = datetime.now()

        sleep_times = []

        for policy in self.policies:

            allowed = is_application_allowed(
                policy,
                current_time,
            )

            if not allowed:

                # During blocked periods, check frequently
                # so newly launched applications are detected.
                sleep_times.append(
                    self.check_interval
                )

                continue

            next_transition = get_next_transition(
                policy,
                current_time,
            )

            if next_transition is not None:

                seconds = (
                    next_transition - current_time
                ).total_seconds()

                sleep_times.append(
                    max(0.1, seconds)
                )

        if not sleep_times:
            return 60.0

        return min(sleep_times)

    def run(self) -> None:

        self.running = True

        while self.running:

            self.enforce_once()

            sleep_time = self.get_sleep_time()

            time_module.sleep(
                sleep_time,
            )

    def stop(self) -> None:
        self.running = False