"""growth-op CLI entry point."""

import asyncio
import re
from datetime import date
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from growth_op_agent.cli.test_commands import test
from growth_op_agent.settings import load_settings

console = Console()
CONFIG_PATH = Path("config/settings.yaml")
BRAND_PATH = Path("config/brand_voice.yaml")
IDEAS_DIR = Path("data/ideas")
X_USERNAME_RE = re.compile(r"^@?[A-Za-z0-9_]{1,15}$")


def _build_orchestrator():
    from growth_op_agent.brand import BrandContext
    from growth_op_agent.data_sources import DataAggregator
    from growth_op_agent.intelligence import IntelligenceLayer
    from growth_op_agent.content import IdeaGenerator
    from growth_op_agent.analytics import PerformanceAnalytics
    from growth_op_agent.orchestrator import Orchestrator

    settings = load_settings(CONFIG_PATH)
    brand = BrandContext.from_yaml(BRAND_PATH)
    intelligence = IntelligenceLayer(brand, model=settings.intelligence.model)
    return Orchestrator(
        IdeaGenerator(intelligence, DataAggregator(), brand),
        PerformanceAnalytics(),
        intelligence,
    )


@click.group()
def cli():
    """GrowthOpAgent — AI-powered content agent."""
    load_dotenv()


@cli.command()
@click.option("--once", is_flag=True, help="Single cycle then exit.")
def run(once: bool):
    """Run the content agent."""
    from growth_op_agent.publishing import PublishScheduler

    console.print(Panel("[bold blue]GrowthOpAgent[/] starting up…", expand=False))
    orchestrator = _build_orchestrator()
    settings = load_settings(CONFIG_PATH)

    if once:
        ideas = asyncio.run(
            orchestrator.run_content_cycle(n=settings.publishing.posts_per_day)
        )
        console.print(f"[green]Content cycle completed with {len(ideas)} ideas.[/]")
        for i, idea in enumerate(ideas, 1):
            console.print(
                f"\n[bold]Idea {i}[/] [{idea.estimated_engagement} engagement]"
            )
            console.print(f"  {idea.content}")
            console.print(f"  [dim]{idea.rationale}[/]")
        return

    scheduler = PublishScheduler(timezone=settings.publishing.timezone)
    scheduler.add_daily_idea_job(
        lambda: asyncio.run(
            orchestrator.run_content_cycle(n=settings.publishing.posts_per_day)
        ),
        hour=6,
    )
    scheduler.add_analytics_job(
        orchestrator.run_analytics_review,
        interval_hours=settings.analytics.performance_review_interval_hours,
    )
    console.print(
        "[green]Scheduler running.[/] Idea JSON saved daily at 06:00. Press Ctrl+C to stop."
    )
    scheduler.start()


@cli.group()
def ideas():
    """Review generated ideas."""


@ideas.command("list")
@click.option(
    "--date", "idea_date", default=None, help="Idea file date in YYYY-MM-DD format."
)
def list_ideas(idea_date: str | None):
    """List generated ideas."""
    from rich.table import Table
    from growth_op_agent.content import IdeaStore

    path = _ideas_path(idea_date)
    records = IdeaStore(path).load()
    if not records:
        raise click.ClickException(
            f"No ideas found at {path}. Run growth-op run --once first."
        )

    table = Table("ID", "Status", "Format", "Engagement", "Content")
    for record in records:
        table.add_row(
            record.id,
            record.status.value,
            record.idea.format,
            record.idea.estimated_engagement,
            _preview(record.idea.content),
        )
    console.print(table)


@ideas.command("reject")
@click.argument("idea_id")
@click.option(
    "--date", "idea_date", default=None, help="Idea file date in YYYY-MM-DD format."
)
def reject_idea(idea_id: str, idea_date: str | None):
    """Reject one generated idea."""
    from growth_op_agent.content import IdeaStatus, IdeaStore

    path = _ideas_path(idea_date)
    store = IdeaStore(path)
    records = store.load()
    if not records:
        raise click.ClickException(
            f"No ideas found at {path}. Run growth-op run --once first."
        )

    for index, record in enumerate(records):
        if record.id == idea_id:
            records[index] = record.transition(IdeaStatus.REJECTED)
            store.save(records)
            console.print(f"[green]Rejected idea {idea_id}.[/]")
            return

    raise click.ClickException(f"Idea {idea_id!r} was not found in {path}.")


@cli.command("import-posts")
@click.option(
    "--handle",
    default=None,
    help="Twitter handle to import (defaults to brand config).",
)
@click.option(
    "--max", "max_results", default=100, show_default=True, help="Max posts to fetch."
)
def import_posts(handle: str | None, max_results: int):
    """Import existing posts from your X account into history.json."""
    from growth_op_agent.analytics import PerformanceAnalytics
    from growth_op_agent.brand import BrandContext

    resolved_handle = handle or BrandContext.from_yaml(BRAND_PATH).handle
    if not X_USERNAME_RE.fullmatch(resolved_handle):
        raise click.ClickException(
            f"Invalid X handle: {resolved_handle!r}. Use an X username like @your_username, "
            "or update brand.handle in config/brand_voice.yaml."
        )

    console.print(
        f"Importing posts for [bold]{resolved_handle}[/] (max {max_results})…"
    )
    try:
        result = PerformanceAnalytics().import_account_posts(
            resolved_handle, max_results
        )
        console.print(
            f"[green]Imported {result.imported} new posts; updated {result.updated} existing posts.[/] "
            "Run [bold]growth-op test snapshot[/] to verify."
        )
    except RuntimeError as e:
        raise click.ClickException(str(e))


@cli.command("record-follow-snapshot")
@click.option("--followers", required=True, type=int, help="Current follower count.")
@click.option(
    "--unfollowers", default=None, type=int, help="Weekly unfollower count, if known."
)
@click.option(
    "--following", default=None, type=int, help="Current following count, if useful."
)
def record_follow_snapshot(
    followers: int,
    unfollowers: int | None,
    following: int | None,
):
    """Record this week's X audience counts."""
    from growth_op_agent.analytics import FollowTracker

    snapshot = FollowTracker().record_weekly_snapshot(
        followers=followers,
        unfollowers=unfollowers,
        following=following,
    )
    console.print(
        f"[green]Recorded week {snapshot.week_of.year}-W{snapshot.week_of.week} audience snapshot.[/] "
        f"followers={snapshot.followers}"
    )


@cli.command("audience-summary")
def audience_summary():
    """Show the latest weekly X audience summary."""
    from growth_op_agent.analytics import FollowTracker

    summary = FollowTracker().latest_summary()
    if not summary:
        raise click.ClickException("No audience snapshots recorded yet.")

    current = summary.current
    console.print(f"Week: {current.week_of.year}-W{current.week_of.week}")
    console.print(f"Followers: {current.followers}")
    if summary.follower_change is not None:
        console.print(f"Follower change: {summary.follower_change:+}")
    if current.unfollowers is not None:
        console.print(f"Unfollowers: {current.unfollowers}")
    if current.following is not None:
        console.print(f"Following: {current.following}")
    if summary.following_change is not None:
        console.print(f"Following change: {summary.following_change:+}")


@cli.command("strategy-update")
def strategy_update():
    """Rewrite strategy_brief from the latest weekly insights (human-reviewed)."""
    from growth_op_agent.brand import BrandContext
    from growth_op_agent.brand.strategy_updater import StrategyUpdater
    from growth_op_agent.intelligence import IntelligenceLayer
    from growth_op_agent.settings import load_settings

    settings = load_settings(CONFIG_PATH)
    brand = BrandContext.from_yaml(BRAND_PATH)
    intelligence = IntelligenceLayer(brand, model=settings.intelligence.model)
    StrategyUpdater(intelligence, brand, BRAND_PATH).run()


@cli.command("voice-update")
def voice_update():
    """Propose voice_brief changes based on rejected ideas (human-reviewed)."""
    from growth_op_agent.brand import BrandContext
    from growth_op_agent.brand.voice_updater import VoiceUpdater
    from growth_op_agent.intelligence import IntelligenceLayer
    from growth_op_agent.settings import load_settings

    settings = load_settings(CONFIG_PATH)
    brand = BrandContext.from_yaml(BRAND_PATH)
    intelligence = IntelligenceLayer(brand, model=settings.intelligence.model)
    VoiceUpdater(intelligence, brand, BRAND_PATH).run()


@cli.command("analytics-review")
@click.option(
    "--force",
    is_flag=True,
    help="Regenerate insights even if this week's already exist.",
)
def analytics_review(force: bool):
    """Run the weekly performance review and save insight snapshot."""
    from growth_op_agent.analytics.weekly_review import latest_insights_path

    console.print("[bold]Running weekly analytics review...[/]")
    try:
        insights = _build_orchestrator().run_analytics_review(force=force)
    except Exception as e:
        raise click.ClickException(str(e))

    path = latest_insights_path()
    if path:
        console.print(f"[green]Weekly insights saved to {path}[/]")
    console.print_json(insights.model_dump_json())


cli.add_command(test)


def _ideas_path(idea_date: str | None) -> Path:
    if idea_date is None:
        return IDEAS_DIR / f"{date.today()}.json"
    try:
        parsed = date.fromisoformat(idea_date)
    except ValueError as e:
        raise click.ClickException("Date must use YYYY-MM-DD format.") from e
    return IDEAS_DIR / f"{parsed}.json"


def _preview(content: str, max_chars: int = 80) -> str:
    text = " ".join(content.split())
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."


def main():
    cli()
