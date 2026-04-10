"""Team OFF/DEF/NET rating panel with league ranks."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED


class TeamStatsPanel(Widget):
    """Team stats panel showing offensive/defensive/net ratings with ranks.

    Displays key team metrics in a compact format.
    """

    DEFAULT_CSS = """
    TeamStatsPanel {
        height: auto;
        width: 100%;
        padding: 0;
    }
    """

    def __init__(
        self,
        off_rtg: float = 0.0,
        def_rtg: float = 0.0,
        net_rtg: float = 0.0,
        pace: float = 0.0,
        off_rank: str = "",
        def_rank: str = "",
        net_rank: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._off_rtg = off_rtg
        self._def_rtg = def_rtg
        self._net_rtg = net_rtg
        self._pace = pace
        self._off_rank = off_rank
        self._def_rank = def_rank
        self._net_rank = net_rank

    def compose(self) -> ComposeResult:
        yield Label("[bold]TEAM STATS[/]")
        off_rank_str = f" ({self._off_rank})" if self._off_rank else ""
        def_rank_str = f" ({self._def_rank})" if self._def_rank else ""
        net_rank_str = f" ({self._net_rank})" if self._net_rank else ""
        net_color = SCORE_GREEN if self._net_rtg > 0 else SCORE_RED
        yield Label(f"  OFF RTG: {self._off_rtg:.1f}{off_rank_str}")
        yield Label(f"  DEF RTG: {self._def_rtg:.1f}{def_rank_str}")
        yield Label(
            f"  NET RTG: [{net_color}]{self._net_rtg:+.1f}[/]{net_rank_str}"
        )
        yield Label(f"  PACE:    {self._pace:.1f}")
