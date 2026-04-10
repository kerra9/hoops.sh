"""Post-Game Summary screen -- final score, leaders, notable performances.

Textual Screen with composed widgets for the end-of-game summary.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from hoops_sim.models.league import League
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.final_score import FinalScoreDisplay
from hoops_sim.tui.widgets.game_leaders import GameLeadersPanel


class PostGameScreen(Screen):
    """Final score, top performers, game log highlights."""

    BINDINGS = [
        Binding("escape", "continue_game", "Continue", show=True),
        Binding("enter", "continue_game", "Continue"),
        Binding("b", "box_score", "Box Score", show=True),
        Binding("c", "continue_game", "Continue"),
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

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="post-game-content"):
                yield FinalScoreDisplay(
                    home_name=self._home_name,
                    away_name=self._away_name,
                    home_score=self._home_score,
                    away_score=self._away_score,
                )

                # Build leaders
                all_stats = list(self._home_stats.player_stats.values()) + list(
                    self._away_stats.player_stats.values()
                )
                leaders = self._build_leaders(all_stats)
                yield GameLeadersPanel(leaders=leaders)

                # Notable performances
                notable_text = self._build_notable(all_stats)
                yield Static(notable_text, markup=True)

                with Vertical():
                    yield Button("Box Score", variant="primary", id="btn-box-score")
                    yield Button("Continue", variant="success", id="btn-continue")
        yield Footer()

    def _build_leaders(self, all_stats):
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
        return leaders

    def _build_notable(self, all_stats) -> str:
        lines = ["[bold]NOTABLE[/]"]
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
        return "\n".join(lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-box-score":
            self.action_box_score()
        elif event.button.id == "btn-continue":
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
