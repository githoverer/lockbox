from datetime import time

from src.lockbox.policy import ApplicationPolicy, TimeWindow
from src.lockbox.storage import PolicyStorage


def test_policy_can_be_saved_and_loaded(tmp_path):

    storage = PolicyStorage(
        tmp_path / "policies.json"
    )

    original = ApplicationPolicy(
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

    storage.save([original])

    loaded = storage.load()

    assert len(loaded) == 1

    assert loaded[0].name == "VALORANT"
    assert loaded[0].executable == "VALORANT-Win64-Shipping.exe"

    window = loaded[0].allowed_windows["sunday"][0]

    assert window.start == time(21, 0)
    assert window.end == time(0, 0)