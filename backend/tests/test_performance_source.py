from datetime import datetime, timezone

from growth_op_agent.analytics import weekly_review
from growth_op_agent.analytics.performance import WeekOf
from growth_op_agent.analytics.weekly_review import WeeklyInsights


def test_latest_insights_path_returns_latest_date(tmp_path, monkeypatch):
    insights_dir = tmp_path / "insights"
    insights_dir.mkdir()
    monkeypatch.setattr(weekly_review, "INSIGHTS_DIR", insights_dir)
    (insights_dir / "weekly_insights_03-05-2026.json").write_text("{}")
    latest = insights_dir / "weekly_insights_04-05-2026.json"
    latest.write_text("{}")

    assert weekly_review.latest_insights_path() == latest


def test_weekly_insights_sync_flattens_week_for_database(monkeypatch):
    calls = []
    monkeypatch.setattr(
        weekly_review,
        "upsert_rows",
        lambda table, rows, on_conflict: calls.append((table, rows, on_conflict)),
    )
    insights = WeeklyInsights(
        week_of=WeekOf(year=2026, week=19),
        generated_at=datetime(2026, 5, 6, 12, tzinfo=timezone.utc),
        strategic_takeaways=["Do more of what works."],
    )

    weekly_review._upsert_insights_to_supabase(insights)

    assert calls == [
        (
            "weekly_insights",
            [
                {
                    "generated_at": "2026-05-06T12:00:00Z",
                    "strategic_takeaways": ["Do more of what works."],
                    "year": 2026,
                    "week": 19,
                }
            ],
            "year,week",
        )
    ]
