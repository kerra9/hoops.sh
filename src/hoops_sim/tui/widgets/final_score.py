"""Large styled final score display."""

from __future__ import annotations

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import SCORE_GREEN


class FinalScoreDisplay(Widget):
    """Large styled final score for the post-game screen."""

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

    def render(self) -> str:
        away_style = f"[bold][{SCORE_GREEN}]" if self._away_score > self._home_score else "[bold]"
        home_style = f"[bold][{SCORE_GREEN}]" if self._home_score > self._away_score else "[bold]"
        return (
            f"[bold]F I N A L[/]\n\n"
            f"  {away_style}{self._away_name:<24} {self._away_score:>3}[/]\n"
            f"  {home_style}{self._home_name:<24} {self._home_score:>3}[/]"
        )
