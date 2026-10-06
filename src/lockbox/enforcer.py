import threading
from datetime import datetime
from typing import Callable

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
        policy_provider: Callable[[], list[ApplicationPolicy]] | None = None,
        policy_reload_interval: float = 1.0,
    ):
        self.policies = policies
        self.check_interval = check_interval
        self.policy_provider = policy_provider
        self.policy_reload_interval = policy_reload_interval

        self.running = False

        # Stops the enforcer completely.
        self.stop_event = threading.Event()

        # Wakes the enforcement loop when policies change.
        self.wake_event = threading.Event()

        self.reload_thread = None

    def reload_policies(self) -> None:

        if self.policy_provider is None:
            return

        try:

            policies = self.policy_provider()

            self.policies = policies

            # Tell the enforcement loop that its current
            # sleep may no longer be valid.
            self.wake_event.set()

        except Exception:
            # Keep the last known good policies.
            pass

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

    def _reload_loop(self) -> None:

        while self.running:

            self.stop_event.wait(
                timeout=self.policy_reload_interval
            )

            if not self.running:
                break

            self.reload_policies()

    def run(self) -> None:

        self.running = True

        self.stop_event.clear()
        self.wake_event.clear()

        if self.policy_provider is not None:

            self.reload_thread = threading.Thread(
                target=self._reload_loop,
                daemon=True,
            )

            self.reload_thread.start()

        while self.running:

            self.enforce_once()

            sleep_time = self.get_sleep_time()

            # Wait until either:
            #
            # 1. The calculated schedule transition occurs.
            # 2. A policy reload wakes us.
            # 3. The service is stopped.
            #
            self.wake_event.wait(
                timeout=sleep_time
            )

            self.wake_event.clear()

    def stop(self) -> None:

        self.running = False

        self.stop_event.set()
        self.wake_event.set()

        if self.reload_thread is not None:

            self.reload_thread.join(
                timeout=2.0
            )