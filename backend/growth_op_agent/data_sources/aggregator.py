"""Aggregates all data sources into a typed Context for the intelligence layer."""

import asyncio

from pydantic import BaseModel

from .hackernews import HackerNewsStory, fetch_hn_top_stories
from .reddit import RedditPost, fetch_all_subreddits, SUBREDDITS


class Context(BaseModel):
    hn_stories: list[HackerNewsStory] = []
    reddit_posts: list[RedditPost] = []


class DataAggregator:
    def __init__(self, subreddits: list[str] = SUBREDDITS) -> None:
        self._subreddits = subreddits

    async def fetch_all(self) -> Context:
        hn_stories, reddit_posts = await asyncio.gather(
            fetch_hn_top_stories(),
            fetch_all_subreddits(self._subreddits),
        )
        return Context(
            hn_stories=hn_stories,
            reddit_posts=reddit_posts,
        )
