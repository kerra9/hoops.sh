"""Week calendar grid for schedule screen.

Textual widget for showing a week of games.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED


class WeekCalendarGrid(Widget):
    """Week calendar grid showing games for each day."""

    def __init__(
        self,
        week_start: int = 1,
        current_day: int = 1,
        day_games: Dict[int, Tuple] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._week_start = week_start
        self._current_day = current_day
        self._day_games = day_games or {}

    def render(self) -> Text:
        text = Text()
        for day_offset in range(7):
            day = self._week_start + day_offset
            is_current = day == self._current_day
            marker = "\u25b6 " if is_current else "  "

            game = self._day_games.get(day)
            if game:
                ha, opp_name, h_score, a_score, is_home = game
                if h_score is not None:
                    if is_home:
                        won = h_score > a_score
                    else:
                        won = a_score > h_score
                    color = SCORE_GREEN if won else SCORE_RED
                    result = f"W" if won else f"L"
                    score_str = f"{a_score}-{h_score}" if is_home else f"{h_score}-{a_score}"
                    text.append(f"{marker}Day {day:>3}: {ha} {opp_name[:12]:<12} ")
                    text.append(f"{result} {score_str}", style=color)
                else:
                    text.append(f"{marker}Day {day:>3}: {ha} {opp_name[:12]}")
            else:
                text.append(f"{marker}Day {day:>3}: --")
            text.append("\n")
        return text
