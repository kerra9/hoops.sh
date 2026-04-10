"""Compact score display for the live game screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class Scoreboard(Widget):
    """Compact score display: team names, score, quarter, game/shot clock.

    Uses reactive properties instead of recompose for efficient updates.
    """

    DEFAULT_CSS = """
    Scoreboard {
        layout: horizontal;
        height: 3;
        align: center middle;
        background: $primary-background;
        padding: 0 2;
        width: 100%;
    }
    """

    home_score: reactive[int] = reactive(0)
    away_score: reactive[int] = reactive(0)

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        home_score: int = 0,
        away_score: int = 0,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name
        self.home_score = home_score
        self.away_score = away_score

    def compose(self) -> ComposeResult:
        with Horizontal(classes="scoreboard"):
            yield Label(self._away_name, classes="scoreboard-team", id="sb-away-name")
            yield Label(
                f"[bold]{self.away_score}[/]",
                classes="scoreboard-score",
                id="sb-away-score",
            )
            yield Label(" - ", classes="scoreboard-divider")
            yield Label(
                f"[bold]{self.home_score}[/]",
                classes="scoreboard-score",
                id="sb-home-score",
            )
            yield Label(self._home_name, classes="scoreboard-team", id="sb-home-name")

    def watch_home_score(self, value: int) -> None:
        """React to home score changes."""
        try:
            self.query_one("#sb-home-score", Label).update(f"[bold]{value}[/]")
        except Exception:
            pass

    def watch_away_score(self, value: int) -> None:
        """React to away score changes."""
        try:
            self.query_one("#sb-away-score", Label).update(f"[bold]{value}[/]")
        except Exception:
            pass

    def update_score(self, home_score: int, away_score: int) -> None:
        """Update the scoreboard."""
        self.home_score = home_score
        self.away_score = away_score
