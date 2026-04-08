"""Post-Game Summary screen -- final score, top performers, highlights."""

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


class PostGameScreen(Screen):
    """Final score, top performers, game log highlights.

    Bridge back to League Hub.
    """

    BINDINGS = [
        ("escape", "continue_game", "Continue"),
        ("enter", "continue_game", "Continue"),
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
                yield Label("FINAL", classes="screen-header")
                yield Label("")
                yield Label(
                    f"  {self._away_name}  {self._away_score}",
                    id="post-away-score",
                )
                yield Label(
                    f"  {self._home_name}  {self._home_score}",
                    id="post-home-score",
                )
                yield Label("")

                # Top performers
                yield Label("Top Performers", classes="conference-header")
                all_stats = list(self._home_stats.player_stats.values()) + list(
                    self._away_stats.player_stats.values()
                )
                top_scorers = sorted(all_stats, key=lambda s: s.points, reverse=True)[:3]
                for ps in top_scorers:
                    yield Label(f"  {ps.player_name}: {ps.stat_line()}")

                yield Label("")

                # Notable performances
                for ps in all_stats:
                    if ps.is_triple_double():
                        yield Label(f"  TRIPLE-DOUBLE: {ps.player_name} ({ps.stat_line()})")
                    elif ps.is_double_double():
                        yield Label(f"  Double-double: {ps.player_name} ({ps.stat_line()})")

                yield Label("")
                yield Button("View Box Score", id="btn-box-score", variant="default")
                yield Button("Continue", id="btn-continue", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-box-score":
            from hoops_sim.tui.screens.box_score import BoxScoreScreen

            self.app.push_screen(
                BoxScoreScreen(
                    home_stats=self._home_stats,
                    away_stats=self._away_stats,
                    home_name=self._home_name,
                    away_name=self._away_name,
                )
            )
        elif event.button.id == "btn-continue":
            self.action_continue_game()

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
