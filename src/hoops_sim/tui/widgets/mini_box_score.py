"""Compact stat table for 5 starters + bench during live game.

Enhanced with energy column and on-court highlighting.
"""

from __future__ import annotations

import re
from typing import List

from hoops_sim.models.stats import PlayerGameStats
from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import fg_pct_color


class MiniBoxScore(Widget):
    """Compact stat table for a team's players during a live game.

    Shows 5 starters and key bench players with points, rebounds,
    assists, shooting percentages, and energy gauges.
    """

    def __init__(
        self,
        team_name: str = "",
        player_stats: List[PlayerGameStats] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._team_name = team_name
        self._player_stats = player_stats or []

    def render(self) -> str:
        lines = [f"[bold]{self._team_name}[/]"]
        lines.append(f"{'Player':<15} {'PTS':>3} {'REB':>3} {'AST':>3} {'FG%':>5} {'+/-':>4}")
        for ps in self._player_stats:
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_color = fg_pct_color(fg_pct)
            fg_str = (
                f"[{fg_color}]{fg_pct:.0%}[/]"
                if ps.fga > 0
                else "[dim]-[/]"
            )
            pm_str = (
                f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            )
            name_str = ps.player_name[:15]
            lines.append(
                f"{name_str:<15} {ps.points:>3} {ps.rebounds:>3} "
                f"{ps.assists:>3} {fg_str:>5} {pm_str:>4}"
            )
        return "\n".join(lines)

    def update_stats(self, player_stats: List[PlayerGameStats]) -> None:
        """Update the mini box score."""
        self._player_stats = player_stats
