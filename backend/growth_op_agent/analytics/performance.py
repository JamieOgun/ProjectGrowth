"""Tracks post performance and computes daily and weekly metrics."""

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import tweepy
from pydantic import BaseModel, Field

from growth_op_agent.supabase import upsert_rows


HISTORY_PATH = Path("data/performance/history.json")


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


class WeeklyMetrics(BaseModel):
    week_of: WeekOf
    computed_at: datetime
    total_posts: int = 0
    avg_likes: float = 0
    avg_retweets: float = 0
    avg_replies: float = 0
    avg_impressions: float = 0
    engagement_rate: float = 0
    top_posts: list[TopPost] = []


class DailyMetrics(BaseModel):
    date: str
    total_posts: int = 0
    avg_likes: float = 0.0
    avg_retweets: float = 0.0
    avg_replies: float = 0.0
    avg_impressions: float = 0.0
    engagement_rate: float = 0.0
    top_posts: list[TopPost] = []
    refreshed_at: datetime | None = None


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
        self.sync_daily_metrics_to_supabase()

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
        self.sync_daily_metrics_to_supabase()
        return ImportPostsResult(imported=imported, updated=updated)

    def compute_weekly_metrics(self) -> WeeklyMetrics:
        """Compute weekly metrics from history-derived daily metrics."""
        computed_at = datetime.now(timezone.utc)
        iso = computed_at.isocalendar()
        cutoff = computed_at.date() - timedelta(days=6)
        daily_metrics = [
            metric
            for metric in build_daily_metrics(self._load(), refreshed_at=computed_at)
            if datetime.fromisoformat(metric.date).date() >= cutoff
        ]
        return WeeklyMetrics(
            week_of=WeekOf(year=iso.year, week=iso.week),
            computed_at=computed_at,
            **_compute_weekly_metrics_from_daily(daily_metrics),
        )

    def sync_daily_metrics_to_supabase(self) -> None:
        rows = [
            metric.model_dump(mode="json")
            for metric in build_daily_metrics(self._load())
        ]
        upsert_rows("daily_metrics", rows, on_conflict="date")

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


def build_daily_metrics(
    posts: list[dict], refreshed_at: datetime | None = None
) -> list[DailyMetrics]:
    refreshed_at = refreshed_at or datetime.now(timezone.utc)
    posts_by_date: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        published_at = _parse_dt(post["published_at"])
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        date_key = published_at.astimezone(timezone.utc).date().isoformat()
        posts_by_date[date_key].append(post)

    metrics = []
    for date_key in sorted(posts_by_date):
        computed = _compute_metrics(posts_by_date[date_key])
        metrics.append(
            DailyMetrics(
                date=date_key,
                refreshed_at=refreshed_at,
                **computed,
            )
        )
    return metrics


def _compute_weekly_metrics_from_daily(metrics: list[DailyMetrics]) -> dict:
    if not metrics:
        return {
            "total_posts": 0,
            "avg_likes": 0.0,
            "avg_retweets": 0.0,
            "avg_replies": 0.0,
            "avg_impressions": 0.0,
            "engagement_rate": 0.0,
            "top_posts": [],
        }

    total_posts = sum(metric.total_posts for metric in metrics)
    if not total_posts:
        return {
            "total_posts": 0,
            "avg_likes": 0.0,
            "avg_retweets": 0.0,
            "avg_replies": 0.0,
            "avg_impressions": 0.0,
            "engagement_rate": 0.0,
            "top_posts": [],
        }

    total_impressions = sum(
        metric.avg_impressions * metric.total_posts for metric in metrics
    )
    total_engagement = sum(
        metric.engagement_rate * metric.avg_impressions * metric.total_posts
        for metric in metrics
    )
    top_posts = sorted(
        (post for metric in metrics for post in metric.top_posts),
        key=lambda post: post.likes,
        reverse=True,
    )[:10]

    return {
        "total_posts": total_posts,
        "avg_likes": round(
            sum(metric.avg_likes * metric.total_posts for metric in metrics)
            / total_posts,
            1,
        ),
        "avg_retweets": round(
            sum(metric.avg_retweets * metric.total_posts for metric in metrics)
            / total_posts,
            1,
        ),
        "avg_replies": round(
            sum(metric.avg_replies * metric.total_posts for metric in metrics)
            / total_posts,
            1,
        ),
        "avg_impressions": round(total_impressions / total_posts, 1),
        "engagement_rate": round(total_engagement / total_impressions, 4)
        if total_impressions
        else 0.0,
        "top_posts": top_posts,
    }


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


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
