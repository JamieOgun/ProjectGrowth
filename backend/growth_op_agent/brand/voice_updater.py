"""CLI-triggered updater that proposes voice_brief changes based on rejected ideas."""

import difflib
from pathlib import Path

import click
from rich.console import Console

from growth_op_agent.brand.brand_context import BrandContext
from growth_op_agent.content.idea_store import IdeaStatus, IdeaStore
from growth_op_agent.intelligence.intelligence import IntelligenceLayer

console = Console()

IDEAS_DIR = Path("data/ideas")


class VoiceUpdater:
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
        rejected = _collect_rejected_posts(IDEAS_DIR)
        if not rejected:
            raise click.ClickException(
                "No rejected ideas found. Reject some ideas first with growth-op ideas reject."
            )

        console.print(f"[dim]Analysing {len(rejected)} rejected post(s)…[/]")

        new_brief = self._intelligence.analyze_rejections(
            rejected, self._brand.voice_brief
        )

        _print_diff(self._brand.voice_brief, new_brief, "voice_brief")

        if not click.confirm("\nApply this update to brand_voice.yaml?"):
            console.print("[yellow]Aborted — no changes written.[/]")
            return

        self._brand.update_voice_brief(new_brief, self._yaml_path)
        console.print("[green]voice_brief updated in brand_voice.yaml.[/]")


def _collect_rejected_posts(ideas_dir: Path) -> list[str]:
    if not ideas_dir.exists():
        return []
    rejected = []
    for path in sorted(ideas_dir.glob("*.json")):
        for record in IdeaStore(path).load():
            if record.status == IdeaStatus.REJECTED:
                rejected.append(record.idea.content)
    return rejected


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
