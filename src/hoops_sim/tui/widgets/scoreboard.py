"""Compact score display for the live game screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label


class Scoreboard(Widget):
    """Compact score display: team names, score, quarter, game/shot clock.

    Reads from GameState.
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
        self._home_score = home_score
        self._away_score = away_score

    def compose(self) -> ComposeResult:
        with Horizontal(classes="scoreboard"):
            yield Label(
                f"{self._away_name}",
                classes="scoreboard-team",
            )
            yield Label(
                f"[bold]{self._away_score}[/]",
                classes="scoreboard-score",
            )
            yield Label(" - ", classes="scoreboard-divider")
            yield Label(
                f"[bold]{self._home_score}[/]",
                classes="scoreboard-score",
            )
            yield Label(
                f"{self._home_name}",
                classes="scoreboard-team",
            )

    def update_score(
        self,
        home_score: int,
        away_score: int,
    ) -> None:
        """Update the scoreboard."""
        self._home_score = home_score
        self._away_score = away_score
        self.refresh(recompose=True)
