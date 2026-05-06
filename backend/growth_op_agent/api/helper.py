import json
from datetime import date, timedelta

from growth_op_agent.api.models import (
    AnalyticsOverview,
    DateRange,
    StatCard,
    WeeklyInsight,
    WeeklyPost,
)


def build_analytics_overview(
    days: int,
    daily_metrics: list[dict],
    audience_metrics: list[dict],
    weekly_insight: dict | None,
) -> AnalyticsOverview:
    start_date = date.today() - timedelta(days=days - 1)
    end_date = date.today()
    total_posts = sum(int(row.get("total_posts") or 0) for row in daily_metrics)
    total_impressions = _weighted_total(daily_metrics, "avg_impressions")
    avg_engagement_rate = _weighted_engagement_rate(daily_metrics)
    follower_series = [
        int(row["followers"])
        for row in audience_metrics
        if row.get("followers") is not None
    ]
    latest_followers = follower_series[-1] if follower_series else 0
    follower_delta = (
        latest_followers - follower_series[0] if len(follower_series) > 1 else 0
    )

    return AnalyticsOverview(
        range=DateRange(
            days=days,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        ),
        stat_cards=[
            StatCard(
                label="impressions",
                value=_format_compact(total_impressions),
                delta="· 0",
                positive=False,
            ),
            StatCard(
                label="followers",
                value=f"{latest_followers:,}",
                delta=_format_signed(follower_delta),
                positive=follower_delta > 0,
            ),
            StatCard(
                label="avg eng. rate",
                value=f"{avg_engagement_rate * 100:.1f}%",
                delta="· 0",
                positive=False,
            ),
            StatCard(
                label="posts",
                value=f"{total_posts} / {days}d",
                delta="· 0",
                positive=False,
            ),
        ],
        follower_series=follower_series,
        engagement_series=[
            round(float(row.get("engagement_rate") or 0) * 100, 1)
            for row in daily_metrics
        ],
        weekly_insight=_map_weekly_insight(weekly_insight),
        posts=_map_posts(daily_metrics),
    )


def _weighted_total(rows: list[dict], field: str) -> int:
    total = 0.0
    for row in rows:
        total += float(row.get(field) or 0) * int(row.get("total_posts") or 0)
    return round(total)


def _weighted_engagement_rate(rows: list[dict]) -> float:
    total_impressions = _weighted_total(rows, "avg_impressions")
    if not total_impressions:
        return 0.0
    engagement = 0.0
    for row in rows:
        engagement += (
            float(row.get("engagement_rate") or 0)
            * float(row.get("avg_impressions") or 0)
            * int(row.get("total_posts") or 0)
        )
    return engagement / total_impressions


def _map_weekly_insight(row: dict | None) -> WeeklyInsight | None:
    if not row:
        return None
    takeaways = row.get("strategic_takeaways") or []
    suggestions = row.get("suggested_content_adjustments") or []
    return WeeklyInsight(
        summary=" ".join(_insight_summary_item(item) for item in takeaways),
        suggestions=[_insight_suggestion_item(item) for item in suggestions],
    )


def _insight_summary_item(item: object) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        takeaway = item.get("takeaway")
        detail = item.get("detail")
        if takeaway and detail:
            return f"{takeaway}: {detail}"
        if takeaway:
            return str(takeaway)
        if detail:
            return str(detail)
    return json.dumps(item, ensure_ascii=False)


def _insight_suggestion_item(item: object) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        adjustment = item.get("adjustment")
        reasoning = item.get("reasoning")
        if adjustment and reasoning:
            return f"{adjustment}: {reasoning}"
        if adjustment:
            return str(adjustment)
        if reasoning:
            return str(reasoning)
    return json.dumps(item, ensure_ascii=False)


def _map_posts(rows: list[dict]) -> list[WeeklyPost]:
    posts = []
    for row in rows:
        for post in row.get("top_posts") or []:
            posts.append(_map_post(post))
    return sorted(posts, key=lambda post: post.impressions, reverse=True)[:10]


def _map_post(post: dict) -> WeeklyPost:
    likes = int(post.get("likes") or 0)
    retweets = int(post.get("retweets") or 0)
    replies = int(post.get("replies") or 0)
    impressions = int(post.get("impressions") or 0)
    engagement = likes + retweets + replies
    published_at = str(post.get("published_at") or "")
    day = date.fromisoformat(published_at[:10]).strftime("%a") if published_at else ""
    return WeeklyPost(
        day=day,
        format=post.get("post_type") or "post",
        hook=_preview(str(post.get("text") or "")),
        impressions=impressions,
        eng=engagement,
        replies=replies,
        rate=round((engagement / impressions) * 100, 1) if impressions else 0.0,
    )


def _format_compact(value: int) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


def _format_signed(value: int) -> str:
    if value > 0:
        return f"+{value:,}"
    if value < 0:
        return f"{value:,}"
    return "· 0"


def _preview(text: str, max_chars: int = 80) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3]}..."
