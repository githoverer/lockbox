from dataclasses import dataclass, field
from datetime import time


@dataclass
class TimeWindow:
    start: time
    end: time

    def to_dict(self) -> dict:
        return {
            "start": self.start.strftime("%H:%M"),
            "end": self.end.strftime("%H:%M"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimeWindow":
        start_hour, start_minute = map(int, data["start"].split(":"))
        end_hour, end_minute = map(int, data["end"].split(":"))

        return cls(
            start=time(start_hour, start_minute),
            end=time(end_hour, end_minute),
        )


@dataclass
class ApplicationPolicy:
    name: str
    executable: str
    allowed_windows: dict[str, list[TimeWindow]] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "executable": self.executable,
            "schedule": {
                day: [window.to_dict() for window in windows]
                for day, windows in self.allowed_windows.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ApplicationPolicy":
        schedule = {
            day: [
                TimeWindow.from_dict(window)
                for window in windows
            ]
            for day, windows in data.get("schedule", {}).items()
        }

        return cls(
            name=data["name"],
            executable=data["executable"],
            allowed_windows=schedule,
        )