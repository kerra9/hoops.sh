"""Large styled final score display.

Textual widget using Rich Text for the post-game final score.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import SCORE_GREEN


class FinalScoreDisplay(Widget):
    """Large styled final score for the post-game screen."""

    def __init__(
        self,
        home_name: str = "Home",
        away_name: str = "Away",
        home_score: int = 0,
        away_score: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._home_name = home_name
        self._away_name = away_name
        self._home_score = home_score
        self._away_score = away_score

    def render(self) -> Text:
        text = Text()
        text.append("F I N A L\n\n", style="bold")
        away_style = f"bold {SCORE_GREEN}" if self._away_score > self._home_score else "bold"
        home_style = f"bold {SCORE_GREEN}" if self._home_score > self._away_score else "bold"
        text.append(f"  {self._away_name:<24} {self._away_score:>3}\n", style=away_style)
        text.append(f"  {self._home_name:<24} {self._home_score:>3}", style=home_style)
        return text
