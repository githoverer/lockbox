import sys
from pathlib import Path

import win32serviceutil
import win32service
import win32event
import servicemanager

# Make the project root available when Windows loads this file
# directly through pywin32.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lockbox.enforcer import LockboxEnforcer
from src.lockbox.storage import PolicyStorage



PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lockbox.enforcer import LockboxEnforcer
from src.lockbox.storage import PolicyStorage




PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "policies.json"


class LockboxService(
    win32serviceutil.ServiceFramework
):

    _svc_name_ = "LockboxService"
    _svc_display_name_ = "Lockbox Application Enforcement"
    _svc_description_ = (
        "Enforces Lockbox application access policies."
    )

    def __init__(self, args):

        super().__init__(args)

        self.stop_event = win32event.CreateEvent(
            None,
            0,
            0,
            None,
        )

        self.enforcer = None

    def SvcStop(self):

        self.ReportServiceStatus(
            win32service.SERVICE_STOP_PENDING
        )

        if self.enforcer is not None:
            self.enforcer.stop()

        win32event.SetEvent(
            self.stop_event
        )

    def SvcDoRun(self):

        storage = PolicyStorage(DATA_FILE)

        policies = storage.load()

        self.enforcer = LockboxEnforcer(
            policies
        )

        self.enforcer.run()


if __name__ == "__main__":

    win32serviceutil.HandleCommandLine(
        LockboxService
    )