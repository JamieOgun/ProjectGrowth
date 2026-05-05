"""Content calendar — maps dates to approved post slots."""

import json
from datetime import date
from pathlib import Path


CALENDAR_PATH = Path("data/calendar/calendar.json")


class ContentCalendar:
    def __init__(self) -> None:
        CALENDAR_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not CALENDAR_PATH.exists():
            CALENDAR_PATH.write_text(json.dumps({}))

    def get_schedule(self, for_date: date | None = None) -> list[str]:
        """Returns approved post times for a given date (ISO format strings)."""
        key = str(for_date or date.today())
        data = json.loads(CALENDAR_PATH.read_text())
        return data.get(key, {}).get("scheduled_times", [])

    def add_slot(self, for_date: date, time_str: str) -> None:
        key = str(for_date)
        data = json.loads(CALENDAR_PATH.read_text())
        entry = data.setdefault(key, {"scheduled_times": []})
        if time_str not in entry["scheduled_times"]:
            entry["scheduled_times"].append(time_str)
        CALENDAR_PATH.write_text(json.dumps(data, indent=2))

    def mark_published(self, for_date: date, time_str: str) -> None:
        key = str(for_date)
        data = json.loads(CALENDAR_PATH.read_text())
        published = data.setdefault(key, {}).setdefault("published", [])
        if time_str not in published:
            published.append(time_str)
        CALENDAR_PATH.write_text(json.dumps(data, indent=2))
