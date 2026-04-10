"""Stat leader display widget."""

from __future__ import annotations

from typing import List, Tuple

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class LeaderBoard(Widget):
    """Stat leader display showing top performers in a category.

    Shows stat name, player name, and value.
    """

    DEFAULT_CSS = """
    LeaderBoard {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        title: str = "LEADERS",
        leaders: List[Tuple[str, str, str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with leader tuples of (stat_abbr, player_name, value_str)."""
        super().__init__(name=name, id=id, classes=classes)
        self._title = title
        self._leaders = leaders or []

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self._title}[/]")
        for stat, player, value in self._leaders:
            yield Label(f"  {stat}: {player} {value}")
        if not self._leaders:
            yield Label("  [dim]No stats yet[/]")

    def update_leaders(self, leaders: List[Tuple[str, str, str]]) -> None:
        """Update the leader board."""
        self._leaders = leaders
        self.refresh(recompose=True)
