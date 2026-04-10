"""Quarter-by-quarter scoring breakdown table."""

from __future__ import annotations

from typing import List

from hoops_sim.tui.base import Widget


class QuarterScoringTable(Widget):
    """Quarter-by-quarter scoring breakdown."""

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        home_quarters: List[int] | None = None,
        away_quarters: List[int] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name
        self._home_q = home_quarters or [0, 0, 0, 0]
        self._away_q = away_quarters or [0, 0, 0, 0]

    def render(self) -> str:
        q_headers = "  ".join(f"Q{i+1}" for i in range(len(self._home_q)))
        home_total = sum(self._home_q)
        away_total = sum(self._away_q)
        away_scores = "  ".join(f"{q:>2}" for q in self._away_q)
        home_scores = "  ".join(f"{q:>2}" for q in self._home_q)
        return (
            f"[bold]QUARTER SCORING[/]\n"
            f"  {'':>12}  {q_headers}  TOTAL\n"
            f"  {self._away_name:>12}  {away_scores}  {away_total:>5}\n"
            f"  {self._home_name:>12}  {home_scores}  {home_total:>5}"
        )
