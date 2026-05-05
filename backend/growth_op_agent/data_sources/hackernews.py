"""Fetches top stories from Hacker News — no API key required."""
import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"


class HackerNewsStory(BaseModel):
    title: str
    url: str
    score: int = 0
    comments: int = 0
    top_comment: str | None = None


async def fetch_hn_top_stories(max_items: int = 10) -> list[HackerNewsStory]:
    async with httpx.AsyncClient(timeout=10) as client:
        top_ids, ai_ids = await asyncio.gather(
            _fetch_top_ids(client, 7),
            _fetch_algolia_ids(client, "AI", 5),
        )

        # Merge: top stories first, AI results fill in, deduplicate
        seen: set[int] = set()
        merged: list[int] = []
        for id_ in top_ids + ai_ids:
            if id_ not in seen:
                seen.add(id_)
                merged.append(id_)

        stories = await asyncio.gather(
            *(_fetch_item(client, id_) for id_ in merged),
            return_exceptions=True,
        )

    valid = [s for s in stories if isinstance(s, HackerNewsStory)]
    return sorted(valid, key=lambda s: s.score, reverse=True)[:max_items]


async def _fetch_top_ids(client: httpx.AsyncClient, n: int) -> list[int]:
    try:
        resp = await client.get(f"{HN_BASE}/topstories.json")
        resp.raise_for_status()
        return resp.json()[:n]
    except Exception as e:
        logger.error("Failed to fetch HN top story IDs: %s", e)
        return []


async def _fetch_algolia_ids(client: httpx.AsyncClient, query: str, n: int) -> list[int]:
    since = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
    try:
        resp = await client.get(
            HN_ALGOLIA,
            params={
                "query": query,
                "tags": "story",
                "hitsPerPage": n,
                "numericFilters": f"created_at_i>{since}",
            },
        )
        resp.raise_for_status()
        return [int(hit["objectID"]) for hit in resp.json().get("hits", [])]
    except Exception as e:
        logger.error("Failed to fetch Algolia HN stories for %r: %s", query, e)
        return []


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> HackerNewsStory | None:
    try:
        resp = await client.get(f"{HN_BASE}/item/{item_id}.json")
        resp.raise_for_status()
        item = resp.json()
        if not item or item.get("type") != "story":
            return None

        # Skip kids[0] (top comment). kids are ordered by HN's ranking,
        # so kids[1] is the second-best comment.
        kids = item.get("kids", [])
        comment_text = await _fetch_comment_text(client, kids[1]) if len(kids) > 1 else None

        return HackerNewsStory(
            title=item.get("title", ""),
            url=item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
            score=item.get("score", 0),
            comments=item.get("descendants", 0),
            top_comment=comment_text,
        )
    except Exception:
        return None


async def _fetch_comment_text(client: httpx.AsyncClient, comment_id: int) -> str | None:
    try:
        resp = await client.get(f"{HN_BASE}/item/{comment_id}.json")
        resp.raise_for_status()
        item = resp.json()
        if not item or item.get("dead") or item.get("deleted"):
            return None
        text = re.sub(r"<[^>]+>", " ", item.get("text", "") or "").strip()
        return text or None
    except Exception:
        return None
