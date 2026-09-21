import json
from pathlib import Path

from .policy import ApplicationPolicy


class PolicyStorage:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, policies: list[ApplicationPolicy]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "applications": [
                policy.to_dict()
                for policy in policies
            ]
        }

        self.path.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8",
        )

    def load(self) -> list[ApplicationPolicy]:
        if not self.path.exists():
            return []

        data = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        return [
            ApplicationPolicy.from_dict(application)
            for application in data.get("applications", [])
        ]