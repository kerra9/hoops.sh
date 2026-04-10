"""Next games list widget for league hub."""

from __future__ import annotations

from typing import List, Tuple

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class MiniSchedule(Widget):
    """Upcoming games list showing next 5 games.

    Displays day, opponent, and home/away indicator.
    """

    DEFAULT_CSS = """
    MiniSchedule {
        height: auto;
        width: 100%;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield Label("[bold]UPCOMING SCHEDULE[/]")
        if self._games:
            for day, ha, opp in self._games[:5]:
                yield Label(f"  Day {day:>3}: {ha} {opp}")
        else:
            yield Label("  [dim]Season complete[/]")

    def update_games(self, games: List[Tuple[int, str, str]]) -> None:
        """Update the schedule list."""
        self._games = games
        self.refresh(recompose=True)
