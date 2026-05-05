"""Wraps the intelligence layer to produce and store daily post ideas."""

from datetime import date
from pathlib import Path

from rich.console import Console

from growth_op_agent.intelligence import IntelligenceLayer
from growth_op_agent.intelligence.intelligence import PostIdea
from growth_op_agent.data_sources import DataAggregator
from growth_op_agent.brand import BrandContext
from growth_op_agent.content.idea_store import IdeaStore

IDEAS_DIR = Path("data/ideas")
console = Console()


class IdeaGenerator:
    def __init__(
        self,
        intelligence: IntelligenceLayer,
        aggregator: DataAggregator,
        brand: BrandContext,
    ) -> None:
        self._intelligence = intelligence
        self._aggregator = aggregator
        self._brand = brand

    async def generate_daily(self, n: int = 10) -> list[PostIdea]:
        console.print("[dim]Fetching data context...[/]")
        context = await self._aggregator.fetch_all()
        console.print(
            "[dim]Fetched context: "
            f"HN={len(context.hn_stories)}, "
            f"Reddit={len(context.reddit_posts)}, "
            f"Performance={'loaded' if context.performance_insights else 'empty'}.[/]"
        )
        console.print(f"[dim]Generating {n} post ideas...[/]")
        ideas = self._intelligence.generate_post_ideas(context, n=n)
        self._persist(ideas)
        console.print(
            f"[dim]Saved idea JSON to {IDEAS_DIR / f'{date.today()}.json'}.[/]"
        )
        return ideas

    def load_pending(self) -> list[PostIdea]:
        path = IDEAS_DIR / f"{date.today()}.json"
        records = IdeaStore(path).load()
        return [record.idea for record in records]

    def _persist(self, ideas: list[PostIdea]) -> None:
        path = IDEAS_DIR / f"{date.today()}.json"
        IdeaStore(path).replace_generated(ideas)
