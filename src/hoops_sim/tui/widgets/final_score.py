"""Large styled final score display."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import SCORE_GREEN


class FinalScoreDisplay(Widget):
    """Large styled final score for the post-game screen.

    Shows both team names and scores with winner highlighted.
    """

    DEFAULT_CSS = """
    FinalScoreDisplay {
        height: auto;
        width: 100%;
        text-align: center;
        padding: 1;
    }
    """

    def __init__(
        self,
        home_name: str = "Home",
        away_name: str = "Away",
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
        yield Label("[bold]F I N A L[/]", id="final-header")
        yield Label("")

        away_style = f"[bold][{SCORE_GREEN}]" if self._away_score > self._home_score else "[bold]"
        away_end = "[/]" if self._away_score > self._home_score else "[/]"
        home_style = f"[bold][{SCORE_GREEN}]" if self._home_score > self._away_score else "[bold]"
        home_end = "[/]" if self._home_score > self._away_score else "[/]"

        yield Label(
            f"  {away_style}{self._away_name:<24} {self._away_score:>3}{away_end}"
        )
        yield Label(
            f"  {home_style}{self._home_name:<24} {self._home_score:>3}{home_end}"
        )
