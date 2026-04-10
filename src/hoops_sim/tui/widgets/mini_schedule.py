"""Next games list widget for league hub."""

from __future__ import annotations

from typing import List, Tuple

from hoops_sim.tui.base import Widget


class MiniSchedule(Widget):
    """Upcoming games list showing next 5 games."""

    def __init__(
        self,
        games: List[Tuple[int, str, str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with game tuples of (day, home_away_str, opponent_name)."""
        super().__init__(name=name, id=id, classes=classes)
        self._games = games or []

    def render(self) -> str:
        lines = ["[bold]UPCOMING SCHEDULE[/]"]
        if self._games:
            for day, ha, opp in self._games[:5]:
                lines.append(f"  Day {day:>3}: {ha} {opp}")
        else:
            lines.append("  [dim]Season complete[/]")
        return "\n".join(lines)

    def update_games(self, games: List[Tuple[int, str, str]]) -> None:
        """Update the schedule list."""
        self._games = games
