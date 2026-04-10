"""Weekly calendar grid for the schedule screen."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import ACCENT_SUCCESS, SCORE_GREEN, SCORE_RED


class WeekCalendarGrid(Widget):
    """Weekly schedule grid showing 7 days at a time.

    Each day cell shows the game (if any), result, and score.
    """

    DEFAULT_CSS = """
    WeekCalendarGrid {
        height: auto;
        width: 100%;
        padding: 0;
    }
    """

    def __init__(
        self,
        week_start: int = 1,
        current_day: int = 1,
        day_games: Dict[int, Tuple[str, str, Optional[int], Optional[int], bool]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with day_games dict of {day: (ha_str, opp_name, home_score, away_score, is_home)}.

        If home_score/away_score are None, game is unplayed.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._week_start = week_start
        self._current_day = current_day
        self._day_games = day_games or {}

    def compose(self) -> ComposeResult:
        yield Label(
            f"  [bold]<< Week starting Day {self._week_start} >>[/]"
        )
        with Vertical():
            for day_offset in range(7):
                day = self._week_start + day_offset
                is_today = day == self._current_day

                if day in self._day_games:
                    ha, opp, h_score, a_score, is_home = self._day_games[day]
                    if h_score is not None and a_score is not None:
                        # Game played
                        if is_home:
                            won = h_score > a_score
                            score_str = f"{a_score}-{h_score}"
                        else:
                            won = a_score > h_score
                            score_str = f"{a_score}-{h_score}"
                        color = SCORE_GREEN if won else SCORE_RED
                        result = "W" if won else "L"
                        yield Label(
                            f"  Day {day:>3} [{color}]{result} {score_str}[/] {ha} {opp}"
                        )
                    else:
                        # Upcoming game
                        marker = f"[{ACCENT_SUCCESS}]TODAY[/] " if is_today else "      "
                        yield Label(f"  Day {day:>3} {marker}{ha} {opp}")
                else:
                    marker = f"[{ACCENT_SUCCESS}]TODAY[/]" if is_today else "[dim]--[/]"
                    yield Label(f"  Day {day:>3} {marker}")

    def update_week(
        self,
        week_start: int,
        current_day: int,
        day_games: Dict[int, Tuple[str, str, Optional[int], Optional[int], bool]],
    ) -> None:
        """Update the calendar week."""
        self._week_start = week_start
        self._current_day = current_day
        self._day_games = day_games
        self.refresh(recompose=True)
