"""Test commands — verify each module in isolation."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

BRAND_PATH = Path("config/brand_voice.yaml")


@click.group()
def test():
    """Test individual modules."""


@test.command()
def brand():
    """Brand context — no keys required."""
    from growth_op_agent.brand import BrandContext

    b = BrandContext.from_yaml(BRAND_PATH)
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column(style="dim")
    table.add_column()
    for field, val in b.model_dump().items():
        table.add_row(field, str(val))
    console.print(table)
    console.rule("System prompt")
    console.print(b.to_system_prompt())


@test.command()
def hn():
    """Hacker News top stories — no keys required."""
    from growth_op_agent.data_sources.hackernews import fetch_hn_top_stories

    stories = asyncio.run(fetch_hn_top_stories(10))
    if not stories:
        raise click.ClickException("No stories returned.")
    console.print_json(json.dumps([story.model_dump(mode="json") for story in stories]))


@test.command()
def reddit():
    """Reddit hot posts — requires ZENROWS_API_KEY."""
    from growth_op_agent.data_sources.reddit import fetch_all_subreddits

    posts = asyncio.run(fetch_all_subreddits(max_posts_each=5))
    if not posts:
        raise click.ClickException("No posts returned — check ZENROWS_API_KEY.")
    console.print_json(json.dumps([post.model_dump(mode="json") for post in posts]))


@test.command("reddit-debug")
@click.option("--subreddit", default="GrowthHacking", show_default=True)
def reddit_debug(subreddit: str):
    """Dump raw shreddit-post attributes for one subreddit — no parsing applied."""
    import httpx
    from bs4 import BeautifulSoup
    from growth_op_agent.data_sources.zenrows import zenrows_get

    async def _fetch():
        url = f"https://www.reddit.com/r/{subreddit}/top/?t=week"
        params = {"js_render": "true", "premium_proxy": "true", "proxy_country": "us"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await zenrows_get(client, url, params=params)
            resp.raise_for_status()
            return resp.text

    html = asyncio.run(_fetch())
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all("shreddit-post")
    if not elements:
        raise click.ClickException(
            "No shreddit-post elements found — page may not have rendered."
        )

    console.print(
        f"[dim]Found {len(elements)} shreddit-post elements. Showing first 2:[/]\n"
    )
    for el in elements[:2]:
        console.print_json(json.dumps(dict(el.attrs)))


@test.command()
def aggregator():
    """Full data aggregator — requires configured data-source keys."""
    from growth_op_agent.data_sources import DataAggregator

    ctx = asyncio.run(DataAggregator().fetch_all())
    table = Table("Source", "Count", box=box.SIMPLE)
    table.add_row("HN stories", str(len(ctx.hn_stories)))
    table.add_row("Reddit posts", str(len(ctx.reddit_posts)))
    table.add_row("Performance", "loaded" if ctx.performance_insights else "empty")
    console.print(table)


@test.command()
def intelligence():
    """Claude intelligence layer — requires ANTHROPIC_API_KEY."""
    from growth_op_agent.brand import BrandContext
    from growth_op_agent.intelligence import IntelligenceLayer
    from growth_op_agent.data_sources.aggregator import Context

    brand = BrandContext.from_yaml(BRAND_PATH)
    intel = IntelligenceLayer(brand)
    ctx = Context()
    console.print("[dim]Calling Claude with a minimal context…[/]\n")
    ideas = intel.generate_post_ideas(ctx, n=2)
    for i, idea in enumerate(ideas, 1):
        console.rule(f"Idea {i} · {idea.format} · [bold]{idea.estimated_engagement}[/]")
        console.print(idea.content)
        console.print(f"\n[dim]{idea.rationale}[/]")


@test.command()
def snapshot():
    """Performance snapshot — no keys required (seeds fake data if empty)."""
    from growth_op_agent.analytics.performance import PerformanceAnalytics

    history_path = Path("data/performance/history.json")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    if not history_path.exists() or json.loads(history_path.read_text()) == []:
        now = datetime.now(timezone.utc).isoformat()
        history_path.write_text(
            json.dumps(
                [
                    {
                        "id": "1",
                        "text": "Post about AI agents",
                        "published_at": now,
                        "likes": 45,
                        "retweets": 8,
                        "replies": 3,
                        "impressions": 900,
                    },
                    {
                        "id": "2",
                        "text": "Insight on product growth",
                        "published_at": now,
                        "likes": 12,
                        "retweets": 2,
                        "replies": 1,
                        "impressions": 300,
                    },
                ]
            )
        )
        console.print("[dim]Seeded fake history.[/]")
    snapshot = PerformanceAnalytics().compute_weekly_snapshot()
    console.print_json(snapshot.model_dump_json())
