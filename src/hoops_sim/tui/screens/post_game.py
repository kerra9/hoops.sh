"""Post-Game Summary screen -- final score, leaders, notable performances."""

from __future__ import annotations

from typing import Optional

from hoops_sim.models.league import League
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.base import Screen
from hoops_sim.tui.widgets.final_score import FinalScoreDisplay
from hoops_sim.tui.widgets.game_leaders import GameLeadersPanel


class PostGameScreen(Screen):
    """Final score, top performers, game log highlights."""

    BINDINGS = [
        ("escape", "continue_game", "Continue"),
        ("enter", "continue_game", "Continue"),
        ("b", "box_score", "Box Score"),
    ]

    def __init__(
        self,
        home_stats: TeamGameStats,
        away_stats: TeamGameStats,
        home_name: str = "Home",
        away_name: str = "Away",
        home_score: int = 0,
        away_score: int = 0,
        league: League | None = None,
        schedule: SeasonSchedule | None = None,
        standings: Standings | None = None,
        seed: int = 42,
    ) -> None:
        super().__init__()
        self._home_stats = home_stats
        self._away_stats = away_stats
        self._home_name = home_name
        self._away_name = away_name
        self._home_score = home_score
        self._away_score = away_score
        self._league = league
        self._schedule = schedule
        self._standings = standings
        self._seed = seed

    def render(self) -> str:
        lines = []

        # Final score
        fsd = FinalScoreDisplay(
            home_name=self._home_name,
            away_name=self._away_name,
            home_score=self._home_score,
            away_score=self._away_score,
        )
        lines.append(fsd.render())
        lines.append("")

        # Game leaders
        all_stats = list(self._home_stats.player_stats.values()) + list(
            self._away_stats.player_stats.values()
        )

        leaders = []
        top_pts = max(all_stats, key=lambda s: s.points, default=None)
        if top_pts:
            leaders.append(("PTS", top_pts.player_name, str(top_pts.points)))
        top_reb = max(all_stats, key=lambda s: s.rebounds, default=None)
        if top_reb:
            leaders.append(("REB", top_reb.player_name, str(top_reb.rebounds)))
        top_ast = max(all_stats, key=lambda s: s.assists, default=None)
        if top_ast:
            leaders.append(("AST", top_ast.player_name, str(top_ast.assists)))
        top_stl = max(all_stats, key=lambda s: s.steals, default=None)
        if top_stl:
            leaders.append(("STL", top_stl.player_name, str(top_stl.steals)))
        top_blk = max(all_stats, key=lambda s: s.blocks, default=None)
        if top_blk:
            leaders.append(("BLK", top_blk.player_name, str(top_blk.blocks)))
        top_3pm = max(all_stats, key=lambda s: s.three_pm, default=None)
        if top_3pm:
            leaders.append(("3PM", top_3pm.player_name, str(top_3pm.three_pm)))

        glp = GameLeadersPanel(leaders=leaders)
        lines.append(glp.render())
        lines.append("")

        # Notable performances
        lines.append("[bold]NOTABLE[/]")
        has_notable = False
        for ps in all_stats:
            if ps.is_triple_double():
                has_notable = True
                lines.append(
                    f"  [bold #9b59b6]TRIPLE-DOUBLE:[/] "
                    f"{ps.player_name} ({ps.stat_line()})"
                )
            elif ps.is_double_double():
                has_notable = True
                lines.append(
                    f"  [bold]Double-double:[/] "
                    f"{ps.player_name} ({ps.stat_line()})"
                )

        if not has_notable:
            top_scorers = sorted(all_stats, key=lambda s: s.points, reverse=True)[:3]
            for ps in top_scorers:
                lines.append(f"  {ps.player_name}: {ps.stat_line()}")

        lines.append("")
        lines.append(
            "  [bold blue][B][/] Box Score  "
            "[bold green][C][/] Continue"
        )
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_box_score()
        elif c in ("c", ""):
            self.action_continue_game()

    def action_box_score(self) -> None:
        from hoops_sim.tui.screens.box_score import BoxScoreScreen

        self.app.push_screen(
            BoxScoreScreen(
                home_stats=self._home_stats,
                away_stats=self._away_stats,
                home_name=self._home_name,
                away_name=self._away_name,
            )
        )

    def action_continue_game(self) -> None:
        """Return to league hub or main menu."""
        if self._league and self._schedule and self._standings:
            from hoops_sim.tui.screens.league_hub import LeagueHubScreen

            self.app.switch_screen(
                LeagueHubScreen(
                    league=self._league,
                    schedule=self._schedule,
                    standings=self._standings,
                    seed=self._seed,
                )
            )
        else:
            from hoops_sim.tui.screens.main_menu import MainMenuScreen

            self.app.switch_screen(MainMenuScreen())
