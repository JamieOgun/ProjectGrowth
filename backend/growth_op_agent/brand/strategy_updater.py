"""CLI-triggered updater that rewrites strategy_brief from the latest weekly insights."""

import difflib
from pathlib import Path

import click
from rich.console import Console

from growth_op_agent.analytics.weekly_review import WeeklyInsights, latest_insights_path
from growth_op_agent.brand.brand_context import BrandContext
from growth_op_agent.intelligence.intelligence import IntelligenceLayer

console = Console()


class StrategyUpdater:
    def __init__(
        self,
        intelligence: IntelligenceLayer,
        brand: BrandContext,
        yaml_path: Path,
    ) -> None:
        self._intelligence = intelligence
        self._brand = brand
        self._yaml_path = yaml_path

    def run(self) -> None:
        path = latest_insights_path()
        if not path:
            raise click.ClickException(
                "No weekly insights found. Run growth-op analytics-review first."
            )

        insights = WeeklyInsights.model_validate_json(path.read_text())
        extra = insights.model_extra or {}
        adjustments: list[str] = extra.get("suggested_content_adjustments", [])
        if not adjustments:
            raise click.ClickException(
                "No suggested_content_adjustments found in the latest insights."
            )

        console.print(f"[dim]Using insights from {path.name}[/]")
        console.print("[bold]Rewriting strategy_brief…[/]")

        new_brief = self._intelligence.rewrite_strategy_brief(
            self._brand.strategy_brief, adjustments
        )

        _print_diff(self._brand.strategy_brief, new_brief, "strategy_brief")

        if not click.confirm("\nApply this update to brand_voice.yaml?"):
            console.print("[yellow]Aborted — no changes written.[/]")
            return

        self._brand.update_strategy_brief(new_brief, self._yaml_path)
        console.print("[green]strategy_brief updated in brand_voice.yaml.[/]")


def _print_diff(old: str, new: str, label: str) -> None:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{label} (current)",
            tofile=f"{label} (proposed)",
        )
    )
    if not diff:
        console.print("[dim]No changes detected.[/]")
        return
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            console.print(f"[green]{line}[/]", end="")
        elif line.startswith("-") and not line.startswith("---"):
            console.print(f"[red]{line}[/]", end="")
        else:
            console.print(line, end="")
