"""Compact score display for the live game screen."""

from __future__ import annotations

from hoops_sim.tui.base import Widget


class Scoreboard(Widget):
    """Compact score display: team names, score, quarter, game/shot clock."""

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

    def render(self) -> str:
        return (
            f"{self._away_name} [bold]{self.away_score}[/]"
            f" - "
            f"[bold]{self.home_score}[/] {self._home_name}"
        )

    def update_score(self, home_score: int, away_score: int) -> None:
        """Update the scoreboard."""
        self.home_score = home_score
        self.away_score = away_score
