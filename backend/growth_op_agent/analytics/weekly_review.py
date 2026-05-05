"""LLM-powered weekly strategic review — runs once per ISO week, persists output."""
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from growth_op_agent.analytics.performance import PerformanceAnalytics, WeekOf

INSIGHTS_DIR = Path("data/performance/insights")
INSIGHTS_NAME_PREFIX = "weekly_insights"


class WeeklyInsights(BaseModel):
    model_config = ConfigDict(extra="allow")  # LLM content passes through as extra fields

    week_of: WeekOf
    generated_at: datetime


class WeeklyReview:
    def __init__(self, intelligence, analytics: PerformanceAnalytics) -> None:
        self._intelligence = intelligence
        self._analytics = analytics

    def run_if_stale(self) -> WeeklyInsights:
        """
        Returns this week's strategic insights.
        Only calls the LLM if insights don't exist for the current ISO week;
        otherwise returns the persisted model untouched.
        """
        current_path = latest_insights_path()
        if current_path and self._is_current():
            return WeeklyInsights.model_validate_json(current_path.read_text())

        self._analytics.refresh_metrics()
        snapshot = self._analytics.compute_weekly_snapshot()

        raw_insights = self._intelligence.review_performance(
            snapshot.model_dump(mode="json", exclude={"week_of", "computed_at"})
        )

        iso = datetime.now(timezone.utc).isocalendar()
        insights = WeeklyInsights(
            week_of=WeekOf(year=iso.year, week=iso.week),
            generated_at=datetime.now(timezone.utc),
            **raw_insights,
        )

        path = _insights_path(insights.generated_at)
        path.write_text(insights.model_dump_json(indent=2))
        return insights

    def _is_current(self) -> bool:
        path = latest_insights_path()
        if not path:
            return False
        insights = WeeklyInsights.model_validate_json(path.read_text())
        iso = datetime.now(timezone.utc).isocalendar()
        return insights.week_of.year == iso.year and insights.week_of.week == iso.week


def latest_insights_path() -> Path | None:
    if not INSIGHTS_DIR.exists():
        return None
    paths = [
        path for path in INSIGHTS_DIR.glob(f"{INSIGHTS_NAME_PREFIX}_*.json")
        if _is_date_insights_path(path)
    ]
    return max(paths, key=_insights_sort_key) if paths else None


def _insights_path(generated_at: datetime) -> Path:
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    date_part = generated_at.strftime("%d-%m-%Y")
    return INSIGHTS_DIR / f"{INSIGHTS_NAME_PREFIX}_{date_part}.json"


def _insights_sort_key(path: Path) -> datetime:
    stem = path.stem
    prefix = f"{INSIGHTS_NAME_PREFIX}_"
    date_part = stem.removeprefix(prefix)
    return datetime.strptime(date_part, "%d-%m-%Y").replace(tzinfo=timezone.utc)


def _is_date_insights_path(path: Path) -> bool:
    try:
        _insights_sort_key(path)
    except ValueError:
        return False
    return True
