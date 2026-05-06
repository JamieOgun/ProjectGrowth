import json
from datetime import datetime, timezone

from growth_op_agent.analytics import performance
from growth_op_agent.analytics.performance import (
    PerformanceAnalytics,
    build_daily_metrics,
)


def test_weekly_metrics_are_built_from_history_daily_metrics(tmp_path, monkeypatch):
    history_path = tmp_path / "history.json"
    monkeypatch.setattr(performance, "HISTORY_PATH", history_path)
    sync_calls = []
    monkeypatch.setattr(
        performance,
        "upsert_rows",
        lambda table, rows, on_conflict: sync_calls.append((table, rows, on_conflict)),
    )

    history_path.write_text(
        json.dumps(
            [
                {
                    "id": "old-post",
                    "text": "Outside window",
                    "published_at": "2026-04-20T09:00:00+00:00",
                    "likes": 100,
                    "retweets": 0,
                    "replies": 0,
                    "impressions": 100,
                },
                {
                    "id": "post-1",
                    "text": "Inside window one",
                    "post_type": "post",
                    "published_at": "2026-05-04T09:00:00+00:00",
                    "conversation_id": "post-1",
                    "referenced_tweets": [],
                    "media": [],
                    "likes": 4,
                    "retweets": 1,
                    "replies": 0,
                    "impressions": 50,
                },
                {
                    "id": "post-2",
                    "text": "Inside window two",
                    "post_type": "reply",
                    "published_at": "2026-05-05T10:00:00+00:00",
                    "conversation_id": "conversation-2",
                    "referenced_tweets": [
                        {"id": "ref-2", "type": "replied_to", "text": "Context"}
                    ],
                    "media": [{"media_key": "media-2", "type": "photo"}],
                    "likes": 8,
                    "retweets": 0,
                    "replies": 2,
                    "impressions": 150,
                },
            ]
        )
    )
    monkeypatch.setattr(
        performance,
        "datetime",
        _fixed_datetime(datetime(2026, 5, 6, 12, tzinfo=timezone.utc)),
    )

    analytics = PerformanceAnalytics()
    metrics = analytics.compute_weekly_metrics()

    assert metrics.week_of.year == 2026
    assert metrics.week_of.week == 19
    assert metrics.total_posts == 2
    assert metrics.avg_likes == 6.0
    assert metrics.avg_retweets == 0.5
    assert metrics.avg_replies == 1.0
    assert metrics.avg_impressions == 100.0
    assert metrics.engagement_rate == 0.075
    assert [post.id for post in metrics.top_posts] == ["post-2", "post-1"]
    assert metrics.top_posts[0].referenced_tweets[0]["text"] == "Context"
    assert metrics.top_posts[0].media[0]["type"] == "photo"
    assert sync_calls == []


def test_build_daily_metrics_groups_history_by_utc_date():
    refreshed_at = datetime(2026, 5, 6, 12, tzinfo=timezone.utc)
    posts = [
        {
            "id": "late-local",
            "text": "Late local post",
            "published_at": "2026-05-04T23:30:00-02:00",
            "likes": 10,
            "retweets": 1,
            "replies": 2,
            "impressions": 100,
        },
        {
            "id": "same-utc-day",
            "text": "Same UTC day",
            "published_at": "2026-05-05T02:00:00+00:00",
            "likes": 2,
            "retweets": 3,
            "replies": 1,
            "impressions": 50,
        },
        {
            "id": "previous-day",
            "text": "Previous day",
            "published_at": "2026-05-04T08:00:00+00:00",
            "likes": 4,
            "retweets": 0,
            "replies": 0,
            "impressions": 40,
        },
    ]

    metrics = build_daily_metrics(posts, refreshed_at=refreshed_at)

    assert [item.date for item in metrics] == ["2026-05-04", "2026-05-05"]
    assert metrics[0].total_posts == 1
    assert metrics[0].avg_likes == 4.0
    assert metrics[0].engagement_rate == 0.1
    assert metrics[1].total_posts == 2
    assert metrics[1].avg_likes == 6.0
    assert metrics[1].avg_retweets == 2.0
    assert metrics[1].avg_replies == 1.5
    assert metrics[1].avg_impressions == 75.0
    assert metrics[1].engagement_rate == 0.1267
    assert [post.id for post in metrics[1].top_posts] == ["late-local", "same-utc-day"]
    assert metrics[1].refreshed_at == refreshed_at


def test_daily_metrics_sync_upserts_all_history_rows(tmp_path, monkeypatch):
    history_path = tmp_path / "history.json"
    monkeypatch.setattr(performance, "HISTORY_PATH", history_path)
    calls = []
    monkeypatch.setattr(
        performance,
        "upsert_rows",
        lambda table, rows, on_conflict: calls.append((table, rows, on_conflict)),
    )
    history_path.write_text(
        json.dumps(
            [
                {
                    "id": "post-1",
                    "text": "one",
                    "published_at": "2026-05-04T09:00:00+00:00",
                    "likes": 3,
                    "retweets": 1,
                    "replies": 0,
                    "impressions": 40,
                },
                {
                    "id": "post-2",
                    "text": "two",
                    "published_at": "2026-05-05T09:00:00+00:00",
                    "likes": 5,
                    "retweets": 0,
                    "replies": 0,
                    "impressions": 50,
                },
            ]
        )
    )

    PerformanceAnalytics().sync_daily_metrics_to_supabase()

    assert len(calls) == 1
    table, rows, on_conflict = calls[0]
    assert table == "daily_metrics"
    assert on_conflict == "date"
    assert [row["date"] for row in rows] == ["2026-05-04", "2026-05-05"]
    assert rows[0]["total_posts"] == 1
    assert rows[0]["avg_likes"] == 3.0
    assert "followers" not in rows[0]
    assert "following" not in rows[0]
    assert "net_followers" not in rows[0]


def _fixed_datetime(now: datetime):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return now.replace(tzinfo=None)
            return now.astimezone(tz)

    return FixedDateTime
