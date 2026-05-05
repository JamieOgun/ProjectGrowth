"""APScheduler wrapper — idea generation and analytics jobs only (no publish jobs)."""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


class PublishScheduler:
    def __init__(self, timezone: str = "UTC") -> None:
        self._scheduler = BlockingScheduler(timezone=timezone)

    def add_daily_idea_job(self, fn, hour: int = 6) -> None:
        self._scheduler.add_job(fn, CronTrigger(hour=hour, minute=0), id="daily_ideas")

    def add_analytics_job(self, fn, interval_hours: int = 24) -> None:
        self._scheduler.add_job(
            fn, "interval", hours=interval_hours, id="analytics_review"
        )

    def start(self) -> None:
        self._scheduler.start()
