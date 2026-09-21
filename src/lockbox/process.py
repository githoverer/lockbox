from pathlib import Path

import psutil


def get_process_name(process: psutil.Process) -> str | None:
    try:
        return process.name()
    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None


def is_process_running(executable: str) -> bool:
    target_name = Path(executable).name.lower()

    for process in psutil.process_iter(["name"]):
        process_name = get_process_name(process)

        if process_name is None:
            continue

        if process_name.lower() == target_name:
            return True

    return False