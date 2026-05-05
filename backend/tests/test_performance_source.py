from datetime import datetime, timezone

from growth_op_agent.analytics import weekly_review
from growth_op_agent.data_sources.performance import OwnPerformanceSource


def test_performance_source_only_returns_weekly_insights(tmp_path, monkeypatch):
    insights_dir = tmp_path / "insights"
    monkeypatch.setattr(weekly_review, "INSIGHTS_DIR", insights_dir)
    insights_path = weekly_review._insights_path(datetime(2026, 5, 4, 9, tzinfo=timezone.utc))
    insights_path.write_text(
        weekly_review.WeeklyInsights(
            week_of={"year": 2026, "week": 19},
            generated_at=datetime(2026, 5, 4, 9, tzinfo=timezone.utc),
            takeaways=["Keep posts concrete"],
            adjustments=["Use more proof"],
        ).model_dump_json()
    )

    context = OwnPerformanceSource().fetch_context()

    assert context == {
        "takeaways": ["Keep posts concrete"],
        "adjustments": ["Use more proof"],
    }


def test_latest_insights_path_returns_latest_date(tmp_path, monkeypatch):
    insights_dir = tmp_path / "insights"
    insights_dir.mkdir()
    monkeypatch.setattr(weekly_review, "INSIGHTS_DIR", insights_dir)
    (insights_dir / "weekly_insights_03-05-2026.json").write_text("{}")
    latest = insights_dir / "weekly_insights_04-05-2026.json"
    latest.write_text("{}")

    assert weekly_review.latest_insights_path() == latest
