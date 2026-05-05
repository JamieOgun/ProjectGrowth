"""Tracks post performance and computes deterministic weekly snapshots."""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import tweepy
from pydantic import BaseModel, Field


HISTORY_PATH = Path("data/performance/history.json")
SNAPSHOT_DIR = Path("data/performance/snapshots")
SNAPSHOT_NAME_PREFIX = "weekly_snapshot"


class WeekOf(BaseModel):
    year: int
    week: int


class TopPost(BaseModel):
    id: str
    text: str
    post_type: str | None = None
    published_at: datetime
    conversation_id: str | None = None
    referenced_tweets: list[dict] = Field(default_factory=list)
    media: list[dict] = Field(default_factory=list)
    likes: int
    retweets: int
    replies: int = 0
    impressions: int = 0


class PerformanceSnapshot(BaseModel):
    week_of: WeekOf
    computed_at: datetime
    audience: dict = Field(default_factory=dict)
    total_posts: int = 0
    avg_likes: float = 0
    avg_retweets: float = 0
    avg_replies: float = 0
    avg_impressions: float = 0
    engagement_rate: float = 0
    top_posts: list[TopPost] = []


@dataclass
class ImportPostsResult:
    imported: int
    updated: int


class PerformanceAnalytics:
    def __init__(self, bearer_token: str | None = None) -> None:
        token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN", "")
        self._client = tweepy.Client(bearer_token=token) if token else None
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not HISTORY_PATH.exists():
            HISTORY_PATH.write_text("[]")

    def record_post(self, post_id: str, text: str) -> None:
        """Save a newly published post for later performance tracking."""
        history = self._load()
        history.append(
            {
                "id": post_id,
                "text": text,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "likes": 0,
                "retweets": 0,
                "replies": 0,
                "impressions": 0,
            }
        )
        self._save(history)

    def refresh_metrics(self) -> None:
        """Pull fresh engagement numbers for all tracked posts from Twitter."""
        if not self._client:
            return
        history = self._load()
        ids = [p["id"] for p in history if p["id"]]
        if not ids:
            return
        # Twitter API allows up to 100 IDs per request
        for chunk in _chunks(ids, 100):
            try:
                tweets = self._client.get_tweets(chunk, tweet_fields=["public_metrics"])
                if not tweets.data:
                    continue
                metrics_by_id = {str(t.id): t.public_metrics for t in tweets.data}
                for post in history:
                    m = metrics_by_id.get(post["id"])
                    if m:
                        post["likes"] = m.get("like_count", 0)
                        post["retweets"] = m.get("retweet_count", 0)
                        post["replies"] = m.get("reply_count", 0)
                        post["impressions"] = m.get("impression_count", 0)
            except Exception:
                continue
        self._save(history)

    def import_account_posts(
        self, handle: str, max_results: int = 100
    ) -> ImportPostsResult:
        """
        Fetch existing posts from a Twitter account and seed history.json.
        Updates posts already present. Returns counts for imported and updated posts.
        """
        if not self._client:
            raise RuntimeError("TWITTER_BEARER_TOKEN is not set.")

        try:
            user = self._client.get_user(
                username=handle.lstrip("@"),
                user_fields=["public_metrics"],
            )
        except (tweepy.TweepyException, requests.RequestException) as e:
            raise RuntimeError(
                f"Could not fetch X user @{handle.lstrip('@')}: {e}"
            ) from e

        if not user.data:
            raise RuntimeError(f"Account @{handle} not found.")
        _record_audience_snapshot(user.data)

        try:
            tweets = self._client.get_users_tweets(
                user.data.id,
                max_results=max_results,
                tweet_fields=[
                    "attachments",
                    "conversation_id",
                    "created_at",
                    "public_metrics",
                    "referenced_tweets",
                ],
                expansions=["attachments.media_keys", "referenced_tweets.id"],
                media_fields=[
                    "alt_text",
                    "media_key",
                    "preview_image_url",
                    "type",
                    "url",
                ],
            )
        except (tweepy.TweepyException, requests.RequestException) as e:
            raise RuntimeError(
                f"Could not fetch posts for @{handle.lstrip('@')}: {e}"
            ) from e

        if not tweets.data:
            return ImportPostsResult(imported=0, updated=0)

        history = self._load()
        history_by_id = {p["id"]: p for p in history}
        included_tweets = {
            str(t.id): t for t in (tweets.includes or {}).get("tweets", [])
        }
        included_media = {
            m.media_key: m for m in (tweets.includes or {}).get("media", [])
        }
        imported = 0
        updated = 0

        for tweet in tweets.data:
            post = _post_from_tweet(tweet, included_tweets, included_media)
            existing = history_by_id.get(post["id"])
            if existing:
                if _merge_post(existing, post):
                    updated += 1
                continue

            history.append(post)
            history_by_id[post["id"]] = post
            imported += 1

        self._save(history)
        return ImportPostsResult(imported=imported, updated=updated)

    def compute_weekly_snapshot(self) -> PerformanceSnapshot:
        """Pure Python — deterministic. Computes metrics for the trailing 7 days and persists."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent = [p for p in self._load() if _parse_dt(p["published_at"]) >= cutoff]
        computed_at = datetime.now(timezone.utc)
        iso = computed_at.isocalendar()
        path = _snapshot_path(computed_at)
        from growth_op_agent.analytics.follow_tracker import FollowTracker

        audience = FollowTracker().latest_summary()
        snapshot = PerformanceSnapshot(
            week_of=WeekOf(year=iso.year, week=iso.week),
            computed_at=computed_at,
            audience=audience.model_dump(mode="json") if audience else {},
            **_compute_metrics(recent),
        )
        path.write_text(snapshot.model_dump_json(indent=2))
        return snapshot

    def snapshot_is_current(self) -> bool:
        """True if a snapshot already exists for the current ISO week."""
        path = latest_snapshot_path()
        if not path:
            return False
        snapshot = PerformanceSnapshot.model_validate_json(path.read_text())
        iso = datetime.now(timezone.utc).isocalendar()
        return snapshot.week_of.year == iso.year and snapshot.week_of.week == iso.week

    def _load(self) -> list[dict]:
        return json.loads(HISTORY_PATH.read_text())

    def _save(self, history: list[dict]) -> None:
        HISTORY_PATH.write_text(json.dumps(history, indent=2))


def _post_from_tweet(tweet, included_tweets: dict, included_media: dict) -> dict:
    m = tweet.public_metrics or {}
    return {
        "id": str(tweet.id),
        "text": tweet.text,
        "post_type": _post_type(tweet),
        "published_at": tweet.created_at.isoformat(),
        "conversation_id": str(tweet.conversation_id)
        if tweet.conversation_id
        else None,
        "referenced_tweets": _referenced_tweets(tweet, included_tweets),
        "media": _media(tweet, included_media),
        "likes": m.get("like_count", 0),
        "retweets": m.get("retweet_count", 0),
        "replies": m.get("reply_count", 0),
        "impressions": m.get("impression_count", 0),
    }


def _merge_post(existing: dict, imported: dict) -> bool:
    changed = False
    for key, value in imported.items():
        if existing.get(key) != value:
            existing[key] = value
            changed = True
    return changed


def _record_audience_snapshot(user) -> None:
    public_metrics = user.public_metrics or {}
    followers = public_metrics.get("followers_count")
    if followers is None:
        return

    from growth_op_agent.analytics.follow_tracker import FollowTracker

    FollowTracker().record_weekly_snapshot(
        followers=followers,
        following=public_metrics.get("following_count"),
    )


def _compute_metrics(posts: list[dict]) -> dict:
    if not posts:
        return {
            "total_posts": 0,
            "avg_likes": 0.0,
            "avg_retweets": 0.0,
            "avg_replies": 0.0,
            "avg_impressions": 0.0,
            "engagement_rate": 0.0,
            "top_posts": [],
        }
    n = len(posts)
    top = sorted(posts, key=lambda p: p.get("likes", 0), reverse=True)[:10]
    total_impressions = sum(p.get("impressions", 0) for p in posts)
    total_engagement = sum(
        p.get("likes", 0) + p.get("retweets", 0) + p.get("replies", 0) for p in posts
    )
    return {
        "total_posts": n,
        "avg_likes": round(sum(p.get("likes", 0) for p in posts) / n, 1),
        "avg_retweets": round(sum(p.get("retweets", 0) for p in posts) / n, 1),
        "avg_replies": round(sum(p.get("replies", 0) for p in posts) / n, 1),
        "avg_impressions": round(total_impressions / n, 1),
        "engagement_rate": round(total_engagement / total_impressions, 4)
        if total_impressions
        else 0.0,
        "top_posts": [
            TopPost(
                id=str(p["id"]),
                text=p["text"],
                post_type=p.get("post_type"),
                published_at=_parse_dt(p["published_at"]),
                conversation_id=p.get("conversation_id"),
                referenced_tweets=p.get("referenced_tweets", []),
                media=p.get("media", []),
                likes=p["likes"],
                retweets=p.get("retweets", 0),
                replies=p.get("replies", 0),
                impressions=p.get("impressions", 0),
            )
            for p in top
        ],
    }


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def latest_snapshot_path() -> Path | None:
    if not SNAPSHOT_DIR.exists():
        return None
    paths = [
        path
        for path in SNAPSHOT_DIR.glob(f"{SNAPSHOT_NAME_PREFIX}_*.json")
        if _is_date_snapshot_path(path)
    ]
    return max(paths, key=_snapshot_sort_key) if paths else None


def _snapshot_path(computed_at: datetime) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    date_part = computed_at.strftime("%d-%m-%Y")
    return SNAPSHOT_DIR / f"{SNAPSHOT_NAME_PREFIX}_{date_part}.json"


def _snapshot_sort_key(path: Path) -> datetime:
    stem = path.stem
    prefix = f"{SNAPSHOT_NAME_PREFIX}_"
    date_part = stem.removeprefix(prefix)
    return datetime.strptime(date_part, "%d-%m-%Y").replace(tzinfo=timezone.utc)


def _is_date_snapshot_path(path: Path) -> bool:
    try:
        _snapshot_sort_key(path)
    except ValueError:
        return False
    return True


def _post_type(tweet) -> str:
    referenced = tweet.referenced_tweets or []
    reference_types = {item.type for item in referenced}
    if "replied_to" in reference_types:
        return "reply"
    if "quoted" in reference_types:
        return "quote"
    if "retweeted" in reference_types:
        return "repost"
    return "post"


def _referenced_tweets(tweet, included_tweets: dict) -> list[dict]:
    referenced = []
    for item in tweet.referenced_tweets or []:
        included = included_tweets.get(str(item.id))
        referenced.append(
            {
                "id": str(item.id),
                "type": item.type,
                "text": included.text if included else None,
            }
        )
    return referenced


def _media(tweet, included_media: dict) -> list[dict]:
    media_keys = (tweet.attachments or {}).get("media_keys", [])
    media = []
    for key in media_keys:
        item = included_media.get(key)
        if not item:
            media.append({"media_key": key})
            continue
        media.append(
            {
                "media_key": key,
                "type": item.type,
                "url": getattr(item, "url", None),
                "preview_image_url": getattr(item, "preview_image_url", None),
                "alt_text": getattr(item, "alt_text", None),
            }
        )
    return media
