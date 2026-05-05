from growth_op_agent.analytics import weekly_review


def test_latest_insights_path_returns_latest_date(tmp_path, monkeypatch):
    insights_dir = tmp_path / "insights"
    insights_dir.mkdir()
    monkeypatch.setattr(weekly_review, "INSIGHTS_DIR", insights_dir)
    (insights_dir / "weekly_insights_03-05-2026.json").write_text("{}")
    latest = insights_dir / "weekly_insights_04-05-2026.json"
    latest.write_text("{}")

    assert weekly_review.latest_insights_path() == latest
