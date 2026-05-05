import json
from datetime import datetime, timezone
from types import SimpleNamespace

from growth_op_agent.analytics import follow_tracker
from growth_op_agent.analytics import performance
from growth_op_agent.analytics.performance import (
    PerformanceAnalytics,
    latest_snapshot_path,
)


def test_weekly_snapshot_uses_date_filename_and_includes_top_10_with_metadata(
    tmp_path, monkeypatch
):
    history_path = tmp_path / "history.json"
    snapshot_dir = tmp_path / "snapshots"
    monkeypatch.setattr(performance, "HISTORY_PATH", history_path)
    monkeypatch.setattr(performance, "SNAPSHOT_DIR", snapshot_dir)
    monkeypatch.setattr(
        follow_tracker.FollowTracker,
        "latest_summary",
        lambda self: SimpleNamespace(
            model_dump=lambda mode: {"current": {"followers": 123}}
        ),
    )

    now = datetime.now(timezone.utc).isoformat()
    history_path.write_text(
        json.dumps(
            [
                {
                    "id": str(i),
                    "text": f"Post {i}",
                    "post_type": "reply" if i % 2 else "post",
                    "published_at": now,
                    "conversation_id": f"conversation-{i}",
                    "referenced_tweets": [
                        {"id": f"ref-{i}", "type": "replied_to", "text": "Context"}
                    ],
                    "media": [
                        {
                            "media_key": f"media-{i}",
                            "type": "photo",
                            "url": "https://example.com/x.jpg",
                        }
                    ],
                    "likes": i,
                    "retweets": 0,
                    "replies": 0,
                    "impressions": 100,
                }
                for i in range(12)
            ]
        )
    )

    analytics = PerformanceAnalytics()
    second = analytics.compute_weekly_snapshot()

    assert len(second.top_posts) == 10
    assert second.top_posts[0].id == "11"
    assert second.top_posts[0].post_type == "reply"
    assert second.top_posts[0].referenced_tweets[0]["text"] == "Context"
    assert second.top_posts[0].media[0]["type"] == "photo"
    assert second.audience["current"]["followers"] == 123
    assert (
        snapshot_dir / f"weekly_snapshot_{datetime.now(timezone.utc):%d-%m-%Y}.json"
    ).exists()


def test_latest_snapshot_path_returns_latest_date(tmp_path, monkeypatch):
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    monkeypatch.setattr(performance, "SNAPSHOT_DIR", snapshot_dir)
    (snapshot_dir / "weekly_snapshot_03-05-2026.json").write_text("{}")
    latest = snapshot_dir / "weekly_snapshot_04-05-2026.json"
    latest.write_text("{}")

    assert latest_snapshot_path() == latest
