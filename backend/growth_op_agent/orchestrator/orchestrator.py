"""Orchestrator — runs the content cycle and weekly analytics review."""
from rich.console import Console

from growth_op_agent.content import IdeaGenerator
from growth_op_agent.analytics import PerformanceAnalytics, WeeklyReview
from growth_op_agent.analytics.weekly_review import WeeklyInsights
from growth_op_agent.intelligence import IntelligenceLayer
from growth_op_agent.intelligence.intelligence import PostIdea

console = Console()


class Orchestrator:
    def __init__(
        self,
        idea_generator: IdeaGenerator,
        analytics: PerformanceAnalytics,
        intelligence: IntelligenceLayer,
    ) -> None:
        self._ideas = idea_generator
        self._analytics = analytics
        self._weekly_review = WeeklyReview(intelligence, analytics)

    async def run_content_cycle(self, n: int = 10) -> list[PostIdea]:
        """Fetch sources and generate ideas as JSON for manual review."""
        console.print("[bold]Starting content cycle...[/]")
        ideas = await self._ideas.generate_daily(n=n)
        return ideas

    def run_analytics_review(self) -> WeeklyInsights:
        """Runs LLM review only if this week's insights don't exist yet."""
        return self._weekly_review.run_if_stale()
