import json
from datetime import datetime, timezone
from types import SimpleNamespace

from growth_op_agent.analytics import follow_tracker, performance
from growth_op_agent.analytics.performance import (
    PerformanceAnalytics,
    _media,
    _merge_post,
    _post_type,
    _referenced_tweets,
)


def test_post_type_detects_reply():
    tweet = SimpleNamespace(
        referenced_tweets=[SimpleNamespace(type="replied_to", id="123")]
    )

    assert _post_type(tweet) == "reply"


def test_post_type_defaults_to_post():
    tweet = SimpleNamespace(referenced_tweets=None)

    assert _post_type(tweet) == "post"


def test_referenced_tweets_includes_context_text_when_returned():
    tweet = SimpleNamespace(
        referenced_tweets=[SimpleNamespace(type="quoted", id="123")]
    )
    included = {"123": SimpleNamespace(text="Original context")}

    assert _referenced_tweets(tweet, included) == [
        {"id": "123", "type": "quoted", "text": "Original context"}
    ]


def test_media_includes_image_metadata_when_returned():
    tweet = SimpleNamespace(attachments={"media_keys": ["media-1"]})
    included = {
        "media-1": SimpleNamespace(
            media_key="media-1",
            type="photo",
            url="https://example.com/image.jpg",
            preview_image_url=None,
            alt_text="Chart screenshot",
        )
    }

    assert _media(tweet, included) == [
        {
            "media_key": "media-1",
            "type": "photo",
            "url": "https://example.com/image.jpg",
            "preview_image_url": None,
            "alt_text": "Chart screenshot",
        }
    ]


def test_merge_post_updates_existing_metadata():
    existing = {
        "id": "123",
        "text": "Existing post",
        "likes": 1,
    }
    imported = {
        "id": "123",
        "text": "Existing post",
        "post_type": "reply",
        "referenced_tweets": [{"id": "456", "type": "replied_to", "text": "Context"}],
        "media": [],
        "likes": 2,
    }

    changed = _merge_post(existing, imported)

    assert changed is True
    assert existing["post_type"] == "reply"
    assert existing["referenced_tweets"][0]["text"] == "Context"
    assert existing["likes"] == 2


def test_import_account_posts_records_follower_snapshot(tmp_path, monkeypatch):
    history_path = tmp_path / "history.json"
    snapshots_path = tmp_path / "follow_snapshots.json"
    history_path.write_text("[]")
    monkeypatch.setattr(performance, "HISTORY_PATH", history_path)
    monkeypatch.setattr(follow_tracker, "FOLLOW_SNAPSHOTS_PATH", snapshots_path)
    sync_calls = []
    monkeypatch.setattr(
        performance,
        "upsert_rows",
        lambda table, rows, on_conflict: sync_calls.append((table, rows, on_conflict)),
    )

    class FakeClient:
        def get_user(self, username, user_fields):
            assert username == "JamieOgundiran"
            assert user_fields == ["public_metrics"]
            return SimpleNamespace(
                data=SimpleNamespace(
                    id="user-1",
                    public_metrics={"followers_count": 123, "following_count": 45},
                )
            )

        def get_users_tweets(self, user_id, **kwargs):
            assert user_id == "user-1"
            tweet = SimpleNamespace(
                id="post-1",
                text="Imported post",
                created_at=datetime(2026, 5, 4, 9, tzinfo=timezone.utc),
                public_metrics={
                    "like_count": 1,
                    "retweet_count": 0,
                    "reply_count": 0,
                    "impression_count": 10,
                },
                conversation_id="post-1",
                referenced_tweets=None,
                attachments=None,
            )
            return SimpleNamespace(data=[tweet], includes={})

    analytics = PerformanceAnalytics()
    analytics._client = FakeClient()

    result = analytics.import_account_posts("@JamieOgundiran")

    snapshots = json.loads(snapshots_path.read_text())
    assert result.imported == 1
    assert snapshots[0]["followers"] == 123
    assert snapshots[0]["following"] == 45
    assert sync_calls[0][0] == "daily_metrics"
    assert sync_calls[0][2] == "date"
    assert sync_calls[0][1][0]["date"] == "2026-05-04"


def test_refresh_metrics_syncs_daily_metrics_after_saving(tmp_path, monkeypatch):
    history_path = tmp_path / "history.json"
    history_path.write_text(
        json.dumps(
            [
                {
                    "id": "post-1",
                    "text": "Existing post",
                    "published_at": "2026-05-04T09:00:00+00:00",
                    "likes": 0,
                    "retweets": 0,
                    "replies": 0,
                    "impressions": 0,
                }
            ]
        )
    )
    monkeypatch.setattr(performance, "HISTORY_PATH", history_path)
    sync_calls = []
    monkeypatch.setattr(
        performance,
        "upsert_rows",
        lambda table, rows, on_conflict: sync_calls.append((table, rows, on_conflict)),
    )

    class FakeClient:
        def get_tweets(self, ids, tweet_fields):
            assert ids == ["post-1"]
            assert tweet_fields == ["public_metrics"]
            tweet = SimpleNamespace(
                id="post-1",
                public_metrics={
                    "like_count": 7,
                    "retweet_count": 1,
                    "reply_count": 2,
                    "impression_count": 100,
                },
            )
            return SimpleNamespace(data=[tweet])

    analytics = PerformanceAnalytics()
    analytics._client = FakeClient()

    analytics.refresh_metrics()

    history = json.loads(history_path.read_text())
    assert history[0]["likes"] == 7
    assert sync_calls[0][0] == "daily_metrics"
    assert sync_calls[0][2] == "date"
    assert sync_calls[0][1][0]["date"] == "2026-05-04"
    assert sync_calls[0][1][0]["avg_likes"] == 7.0
