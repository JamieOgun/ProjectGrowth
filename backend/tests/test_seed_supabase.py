import json

from scripts import seed_supabase


def test_seed_daily_metrics_uses_history_posts(tmp_path, monkeypatch):
    performance_dir = tmp_path / "performance"
    performance_dir.mkdir()
    (performance_dir / "history.json").write_text(
        json.dumps(
            [
                {
                    "id": "post-1",
                    "text": "one",
                    "published_at": "2026-05-04T09:00:00+00:00",
                    "likes": 4,
                    "retweets": 1,
                    "replies": 0,
                    "impressions": 50,
                },
                {
                    "id": "post-2",
                    "text": "two",
                    "published_at": "2026-05-04T11:00:00+00:00",
                    "likes": 2,
                    "retweets": 0,
                    "replies": 1,
                    "impressions": 50,
                },
            ]
        )
    )
    calls = []
    monkeypatch.setattr(seed_supabase, "PERFORMANCE_DIR", performance_dir)
    monkeypatch.setattr(
        seed_supabase,
        "_post",
        lambda table, rows, on_conflict=None: calls.append((table, rows, on_conflict)),
    )

    seed_supabase.seed_daily_metrics()

    assert len(calls) == 1
    table, rows, on_conflict = calls[0]
    assert table == "daily_metrics"
    assert on_conflict == "date"
    assert len(rows) == 1
    assert rows[0]["date"] == "2026-05-04"
    assert rows[0]["total_posts"] == 2
    assert rows[0]["avg_likes"] == 3.0
    assert rows[0]["engagement_rate"] == 0.08


def test_seed_main_runs_only_selected_targets(monkeypatch):
    calls = []
    monkeypatch.setattr(
        seed_supabase,
        "SEEDERS",
        {
            "posts": lambda: calls.append("posts"),
            "daily_metrics": lambda: calls.append("daily_metrics"),
        },
    )

    seed_supabase.main(["daily_metrics"])

    assert calls == ["daily_metrics"]


def test_seed_headers_use_write_key(monkeypatch):
    monkeypatch.setattr(seed_supabase, "WRITE_KEY", "service-role-key")

    headers = seed_supabase._headers(merge=True)

    assert headers["apikey"] == "service-role-key"
    assert headers["Authorization"] == "Bearer service-role-key"
    assert headers["Prefer"] == "resolution=merge-duplicates,return=minimal"
