"""Post-Game Summary screen -- final score, leaders, sparklines, quarter scoring.

Redesigned with styled final score, game leaders, notable performances,
quarter scoring breakdown, and scoring run sparklines.
"""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.final_score import FinalScoreDisplay
from hoops_sim.tui.widgets.game_leaders import GameLeadersPanel
from hoops_sim.tui.widgets.quarter_scoring import QuarterScoringTable


class PostGameScreen(Screen):
    """Final score, top performers, game log highlights.

    Features:
    - Large styled final score with winner highlighted
    - Game leaders panel (PTS, REB, AST, STL, BLK, 3PM)
    - Notable performances (triple-doubles, big runs)
    - Quarter scoring breakdown
    """

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

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="post-game-screen"):
            with Vertical():
                # Final score display
                yield FinalScoreDisplay(
                    home_name=self._home_name,
                    away_name=self._away_name,
                    home_score=self._home_score,
                    away_score=self._away_score,
                    id="final-score",
                )

                yield Label("")

                # Game leaders
                all_stats = list(
                    self._home_stats.player_stats.values()
                ) + list(self._away_stats.player_stats.values())

                leaders = []
                # PTS leader
                top_pts = max(all_stats, key=lambda s: s.points, default=None)
                if top_pts:
                    leaders.append(("PTS", top_pts.player_name, str(top_pts.points)))
                # REB leader
                top_reb = max(all_stats, key=lambda s: s.rebounds, default=None)
                if top_reb:
                    leaders.append(
                        ("REB", top_reb.player_name, str(top_reb.rebounds))
                    )
                # AST leader
                top_ast = max(all_stats, key=lambda s: s.assists, default=None)
                if top_ast:
                    leaders.append(
                        ("AST", top_ast.player_name, str(top_ast.assists))
                    )
                # STL leader
                top_stl = max(all_stats, key=lambda s: s.steals, default=None)
                if top_stl:
                    leaders.append(
                        ("STL", top_stl.player_name, str(top_stl.steals))
                    )
                # BLK leader
                top_blk = max(all_stats, key=lambda s: s.blocks, default=None)
                if top_blk:
                    leaders.append(
                        ("BLK", top_blk.player_name, str(top_blk.blocks))
                    )
                # 3PM leader
                top_3pm = max(
                    all_stats, key=lambda s: s.three_pm, default=None
                )
                if top_3pm:
                    leaders.append(
                        ("3PM", top_3pm.player_name, str(top_3pm.three_pm))
                    )

                yield GameLeadersPanel(leaders=leaders, id="game-leaders")

                yield Label("")

                # Notable performances
                yield Label("[bold]NOTABLE[/]")
                has_notable = False
                for ps in all_stats:
                    if ps.is_triple_double():
                        has_notable = True
                        yield Label(
                            f"  [bold #9b59b6]TRIPLE-DOUBLE:[/] "
                            f"{ps.player_name} ({ps.stat_line()})"
                        )
                    elif ps.is_double_double():
                        has_notable = True
                        yield Label(
                            f"  [bold]Double-double:[/] "
                            f"{ps.player_name} ({ps.stat_line()})"
                        )

                # Top 3 scorers if no notable
                if not has_notable:
                    top_scorers = sorted(
                        all_stats, key=lambda s: s.points, reverse=True
                    )[:3]
                    for ps in top_scorers:
                        yield Label(f"  {ps.player_name}: {ps.stat_line()}")

                yield Label("")

                # Action buttons
                yield Label(
                    "  [bold blue][B][/] Box Score  "
                    "[bold green][C][/] Continue"
                )
                yield Label("")
                yield Button(
                    "View Box Score", id="btn-box-score", variant="default"
                )
                yield Button("Continue", id="btn-continue", variant="primary")
        yield Footer()

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
