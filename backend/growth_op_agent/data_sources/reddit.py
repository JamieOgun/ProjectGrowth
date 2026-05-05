"""Fetches top posts from target subreddits via ZenRows with JS rendering."""
import asyncio
import logging

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from .zenrows import zenrows_get

logger = logging.getLogger(__name__)

SUBREDDITS = [
    "AgentsOfAI",
    "GrowthHacking",
    "singularity",
    "ClaudeAI",
]

DEFAULT_MAX_POSTS = 5
_JSON_HEADERS = {"User-Agent": "GrowthOpAgent/1.0"}


class RedditPost(BaseModel):
    title: str
    url: str
    subreddit: str
    votes: int = 0
    num_comments: int = 0
    post_type: str | None = None
    image_url: str | None = None
    body: str | None = None


def _parse_subreddit_page(html: str, subreddit_name: str, max_posts: int) -> list[RedditPost]:
    soup = BeautifulSoup(html, "html.parser")
    posts = []

    for el in soup.find_all("shreddit-post"):
        if len(posts) >= max_posts:
            break
        title = el.get("post-title", "").strip()
        permalink = el.get("permalink", "")
        if not title:
            continue
        try:
            votes = int(el.get("score", 0))
            num_comments = int(el.get("comment-count", 0))
        except (ValueError, TypeError):
            votes, num_comments = 0, 0
        post_type = el.get("post-type") or None
        content_href = el.get("content-href", "")
        image_url = content_href if post_type == "image" else None
        posts.append(RedditPost(
            title=title,
            url=f"https://www.reddit.com{permalink}",
            subreddit=subreddit_name,
            votes=votes,
            num_comments=num_comments,
            post_type=post_type,
            image_url=image_url,
        ))

    return posts


async def _fetch_post_body(client: httpx.AsyncClient, post: RedditPost) -> RedditPost:
    """Fetch selftext for non-image posts via Reddit's public JSON endpoint."""
    if post.image_url:
        return post
    try:
        resp = await client.get(f"{post.url}.json", headers=_JSON_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        selftext = data[0]["data"]["children"][0]["data"].get("selftext", "").strip()
        return post.model_copy(update={"body": selftext or None})
    except Exception:
        return post


async def fetch_subreddit_posts(
    subreddit_name: str,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    max_posts: int = DEFAULT_MAX_POSTS,
) -> list[RedditPost]:
    url = f"https://www.reddit.com/r/{subreddit_name}/top/?t=week"
    params = {
        "js_render": "true",
        "premium_proxy": "true",
        "proxy_country": "us",
    }
    async with semaphore:
        try:
            response = await zenrows_get(client, url, params=params)
            response.raise_for_status()
        except Exception as e:
            logger.error("Error fetching r/%s: %s", subreddit_name, e)
            return []

    posts = _parse_subreddit_page(response.text, subreddit_name, max_posts)
    enriched = await asyncio.gather(*(_fetch_post_body(client, p) for p in posts))
    logger.info("r/%s — found %d posts", subreddit_name, len(enriched))
    return list(enriched)


async def fetch_all_subreddits(
    subreddits: list[str] = SUBREDDITS,
    max_posts_each: int = DEFAULT_MAX_POSTS,
) -> list[RedditPost]:
    semaphore = asyncio.Semaphore(3)  # max 3 concurrent ZenRows requests
    async with httpx.AsyncClient(timeout=60) as client:
        results = await asyncio.gather(
            *(fetch_subreddit_posts(s, client, semaphore, max_posts_each) for s in subreddits),
            return_exceptions=True,
        )
    posts: list[RedditPost] = []
    for result in results:
        if isinstance(result, list):
            posts.extend(result)
    return posts
