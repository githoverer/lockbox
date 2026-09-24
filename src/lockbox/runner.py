from pathlib import Path

from .enforcer import LockboxEnforcer
from .storage import PolicyStorage


DATA_FILE = Path("data/policies.json")


def main():

    storage = PolicyStorage(DATA_FILE)

    policies = storage.load()

    print(
        f"Loaded {len(policies)} application policy(s)."
    )

    for policy in policies:
        print(
            f"- {policy.name}: "
            f"{policy.executable}"
        )

    if not policies:
        print("No policies configured.")
        return

    enforcer = LockboxEnforcer(policies)

    print()
    print("Lockbox enforcement started.")
    print("Press Ctrl+C to stop.")

    try:
        enforcer.run()

    except KeyboardInterrupt:
        print()
        print("Stopping Lockbox...")
        enforcer.stop()


if __name__ == "__main__":
    main()