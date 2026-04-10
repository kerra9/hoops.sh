"""Live Game screen -- real-time play-by-play simulation.

Textual Screen with async simulation worker, composed widgets,
and reactive state management. The centerpiece of the TUI.
"""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.simulator import GameSimulator
from hoops_sim.models.league import League
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.models.team import Team
from hoops_sim.narration.engine import NarrationIntensity
from hoops_sim.psychology.momentum import MomentumTracker
from hoops_sim.season.schedule import ScheduledGame, SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.messages import SimCourtUpdate, SimGameOver, SimNarration, SimTick
from hoops_sim.tui.widgets.broadcast_scoreboard import BroadcastScoreboard
from hoops_sim.tui.widgets.context_strip import ContextStrip
from hoops_sim.tui.widgets.court_map import CourtMap
from hoops_sim.tui.widgets.mini_box_score import MiniBoxScoreWidget
from hoops_sim.tui.widgets.play_by_play import PlayByPlayWidget
from hoops_sim.tui.workers import SimulationWorker
from hoops_sim.utils.rng import SeededRNG


class LiveGameScreen(Screen):
    """The main event: real-time play-by-play simulation.

    Uses an async SimulationWorker that runs the GameSimulator in the
    background, posting messages to the UI for reactive widget updates.
    """

    BINDINGS = [
        Binding("space", "toggle_pause", "Pause/Resume", show=True),
        Binding("f", "fast_forward", "Fast", show=True),
        Binding("s", "slow_down", "Slow", show=True),
        Binding("i", "instant_sim", "Instant", show=True),
        Binding("b", "toggle_box_score", "Box Score", show=True),
        Binding("q", "end_game", "End Game", show=True),
    ]

    def __init__(
        self,
        home_team: Team | None = None,
        away_team: Team | None = None,
        scheduled_game: ScheduledGame | None = None,
        league: League | None = None,
        standings: Standings | None = None,
        schedule: SeasonSchedule | None = None,
        seed: int = 42,
    ) -> None:
        super().__init__()
        self._home_team = home_team
        self._away_team = away_team
        self._scheduled_game = scheduled_game
        self._league = league
        self._standings = standings
        self._schedule = schedule
        self._seed = seed
        self._game_over = False
        self._worker: SimulationWorker | None = None
        self._sim_task: asyncio.Task | None = None

        # Create the real GameSimulator
        if home_team and away_team:
            self._simulator = GameSimulator(
                home_team=home_team,
                away_team=away_team,
                seed=seed,
                narrate=True,
            )
        else:
            self._simulator = None

        # Expose stats from the simulator (or empty if no teams)
        if self._simulator:
            self._home_stats = self._simulator.home_stats
            self._away_stats = self._simulator.away_stats
            self._game_state = self._simulator.game_state
            self._momentum = self._simulator.momentum
        else:
            self._home_stats = TeamGameStats(team_id=0, team_name="Home")
            self._away_stats = TeamGameStats(team_id=0, team_name="Away")
            self._game_state = GameState()
            self._momentum = MomentumTracker()

    def compose(self) -> ComposeResult:
        home_name = self._home_team.full_name if self._home_team else "Home"
        away_name = self._away_team.full_name if self._away_team else "Away"
        home_abbr = self._home_team.abbreviation if self._home_team else "HME"
        away_abbr = self._away_team.abbreviation if self._away_team else "AWY"

        yield Header()
        with Vertical(id="live-game"):
            yield BroadcastScoreboard(
                home_name=home_name,
                away_name=away_name,
                home_abbr=home_abbr,
                away_abbr=away_abbr,
                id="live-game-scoreboard",
            )
            with Horizontal(id="live-game-body"):
                yield CourtMap(id="live-game-court")
                yield PlayByPlayWidget(id="live-game-pbp")
            yield ContextStrip(
                home_name=home_name,
                away_name=away_name,
                id="live-game-context",
            )
        yield Footer()

    def on_mount(self) -> None:
        """Start the simulation when the screen mounts."""
        if self._simulator:
            self._worker = SimulationWorker(self._simulator)
            pbp = self.query_one("#live-game-pbp", PlayByPlayWidget)
            home_name = self._home_team.full_name if self._home_team else "Home"
            away_name = self._away_team.full_name if self._away_team else "Away"
            pbp.add_text(
                f"Welcome to {home_name} vs {away_name}!",
                NarrationIntensity.HIGH,
            )
            pbp.add_text("Tip-off!", NarrationIntensity.MEDIUM)
            self._sim_task = asyncio.create_task(self._worker.run(self))

    def on_sim_tick(self, message: SimTick) -> None:
        """Handle simulation tick updates."""
        scoreboard = self.query_one("#live-game-scoreboard", BroadcastScoreboard)
        scoreboard.update_state(
            home_score=message.home_score,
            away_score=message.away_score,
            quarter=message.quarter,
            game_clock=message.game_clock,
            shot_clock=message.shot_clock,
            is_overtime=message.is_overtime,
        )
        context = self.query_one("#live-game-context", ContextStrip)
        context.update_context(momentum=message.momentum)

    def on_sim_narration(self, message: SimNarration) -> None:
        """Handle narration events."""
        pbp = self.query_one("#live-game-pbp", PlayByPlayWidget)
        pbp.add_event(message.event)

    def on_sim_court_update(self, message: SimCourtUpdate) -> None:
        """Handle court position updates."""
        court = self.query_one("#live-game-court", CourtMap)
        court.update_positions(
            offense=message.offense,
            defense=message.defense,
            ball_carrier=message.ball_carrier,
        )

    def on_sim_game_over(self, message: SimGameOver) -> None:
        """Handle game over."""
        self._game_over = True
        pbp = self.query_one("#live-game-pbp", PlayByPlayWidget)
        pbp.add_text(
            f"FINAL: {message.away_score} - {message.home_score}",
            NarrationIntensity.MAXIMUM,
        )
        self._record_game_result()
        self.app.notify("Game Over!")

    def _record_game_result(self) -> None:
        """Record the game result in schedule and standings."""
        gs = self._game_state
        if self._scheduled_game and not self._scheduled_game.played:
            self._scheduled_game.record_result(gs.score.home, gs.score.away)

            if self._standings and self._home_team and self._away_team:
                same_conf = self._home_team.conference == self._away_team.conference
                same_div = self._home_team.division == self._away_team.division
                self._standings.record_game(
                    self._home_team.id,
                    self._away_team.id,
                    gs.score.home,
                    gs.score.away,
                    is_home_win=gs.score.home > gs.score.away,
                    is_conference=same_conf,
                    is_division=same_div,
                )

    def action_toggle_pause(self) -> None:
        """Pause or resume the simulation."""
        if self._worker:
            if self._worker.paused:
                self._worker.resume()
                self.app.notify("Resumed")
            else:
                self._worker.pause()
                self.app.notify("Paused")

    def action_fast_forward(self) -> None:
        """Increase simulation speed."""
        if self._worker:
            current = self._worker._delay
            new_delay = max(0.0, current / 2)
            self._worker.set_speed(new_delay)
            self.app.notify(f"Speed: {new_delay:.2f}s/tick")

    def action_slow_down(self) -> None:
        """Decrease simulation speed."""
        if self._worker:
            current = self._worker._delay
            new_delay = min(4.0, current * 2 if current > 0 else 0.5)
            self._worker.set_speed(new_delay)
            self.app.notify(f"Speed: {new_delay:.2f}s/tick")

    def action_instant_sim(self) -> None:
        """Run simulation instantly."""
        if self._worker:
            self._worker.set_speed(0.0)
            self.app.notify("Instant simulation")

    def action_toggle_box_score(self) -> None:
        """Show box score."""
        from hoops_sim.tui.screens.box_score import BoxScoreScreen

        self.app.push_screen(
            BoxScoreScreen(
                home_stats=self._home_stats,
                away_stats=self._away_stats,
                home_name=self._home_team.full_name if self._home_team else "Home",
                away_name=self._away_team.full_name if self._away_team else "Away",
            )
        )

    def action_end_game(self) -> None:
        """End the game and go to post-game summary."""
        if self._worker:
            self._worker.cancel()
        self._game_over = True
        self._record_game_result()

        from hoops_sim.tui.screens.post_game import PostGameScreen

        self.app.switch_screen(
            PostGameScreen(
                home_stats=self._home_stats,
                away_stats=self._away_stats,
                home_name=self._home_team.full_name if self._home_team else "Home",
                away_name=self._away_team.full_name if self._away_team else "Away",
                home_score=self._game_state.score.home,
                away_score=self._game_state.score.away,
                league=self._league,
                schedule=self._schedule,
                standings=self._standings,
                seed=self._seed,
            )
        )

    def on_unmount(self) -> None:
        """Clean up the worker when leaving the screen."""
        if self._worker:
            self._worker.cancel()
        if self._sim_task and not self._sim_task.done():
            self._sim_task.cancel()

    # Backward-compatible method for synchronous usage
    def run_game(self) -> None:
        """Run the full game simulation synchronously (for non-TUI use)."""
        if self._simulator is None:
            return
        while not self._simulator.is_game_over:
            self._simulator.step()
