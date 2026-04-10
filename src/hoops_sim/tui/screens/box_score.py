"""Box Score screen -- tabbed traditional + advanced stats."""

from __future__ import annotations

from hoops_sim.models.stats import TeamGameStats
from hoops_sim.tui.base import Screen
from hoops_sim.tui.theme import fg_pct_color
from hoops_sim.tui.widgets.quarter_scoring import QuarterScoringTable


class BoxScoreScreen(Screen):
    """Traditional + advanced box score from PlayerGameStats / TeamGameStats."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(
        self,
        home_stats: TeamGameStats,
        away_stats: TeamGameStats,
        home_name: str = "Home",
        away_name: str = "Away",
        home_quarters: list[int] | None = None,
        away_quarters: list[int] | None = None,
    ) -> None:
        super().__init__()
        self._home_stats = home_stats
        self._away_stats = away_stats
        self._home_name = home_name
        self._away_name = away_name
        self._home_quarters = home_quarters or []
        self._away_quarters = away_quarters or []

    def render(self) -> str:
        home_total = sum(ps.points for ps in self._home_stats.player_stats.values())
        away_total = sum(ps.points for ps in self._away_stats.player_stats.values())

        lines = [
            f"[bold]Box Score -- {self._away_name} {away_total} vs {self._home_name} {home_total}[/]",
            "",
        ]

        header = (
            f"{'Player':<18} {'MIN':>3} {'PTS':>3} {'REB':>3} {'AST':>3} "
            f"{'STL':>3} {'BLK':>3} {'FGM-A':>6} {'FG%':>6} {'3PM-A':>6} "
            f"{'FTM-A':>6} {'TO':>3} {'+/-':>4}"
        )

        lines.append(f"\n[bold]{self._away_name}[/]")
        lines.append(header)
        lines.extend(self._render_team(self._away_stats))

        lines.append(f"\n[bold]{self._home_name}[/]")
        lines.append(header)
        lines.extend(self._render_team(self._home_stats))

        if self._home_quarters or self._away_quarters:
            lines.append("")
            qt = QuarterScoringTable(
                home_name=self._home_name,
                away_name=self._away_name,
                home_quarters=self._home_quarters,
                away_quarters=self._away_quarters,
            )
            lines.append(qt.render())

        lines.append("\n  [bold red][B][/] Back")
        return "\n".join(lines)

    def _render_team(self, team_stats: TeamGameStats) -> list[str]:
        rows = []
        for ps in sorted(
            team_stats.player_stats.values(),
            key=lambda s: s.minutes,
            reverse=True,
        ):
            pm_str = f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_color = fg_pct_color(fg_pct)
            fg_pct_str = f"[{fg_color}]{fg_pct:.3f}[/]" if ps.fga > 0 else "-"

            name_str = ps.player_name[:18]
            if ps.is_triple_double():
                name_str = f"[bold #9b59b6]{name_str}[/]"
            elif ps.is_double_double():
                name_str = f"[bold]{name_str}[/]"

            rows.append(
                f"{name_str:<18} {ps.minutes:>3.0f} {ps.points:>3} {ps.rebounds:>3} "
                f"{ps.assists:>3} {ps.steals:>3} {ps.blocks:>3} "
                f"{ps.fgm}-{ps.fga:>5} {fg_pct_str:>6} "
                f"{ps.three_pm}-{ps.three_pa:>5} {ps.ftm}-{ps.fta:>5} "
                f"{ps.turnovers:>3} {pm_str:>4}"
            )
        return rows

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
