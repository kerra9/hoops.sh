"""Live Game screen -- real-time play-by-play simulation.

Now powered by the real GameSimulator instead of random dice rolls.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.simulator import GameSimulator, SimEvent
from hoops_sim.engine.tick import TickEventType
from hoops_sim.models.league import League
from hoops_sim.models.stats import PlayerGameStats, TeamGameStats
from hoops_sim.models.team import Team
from hoops_sim.narration.engine import NarrationEngine, NarrationEvent, NarrationIntensity
from hoops_sim.psychology.momentum import MomentumTracker
from hoops_sim.season.schedule import ScheduledGame, SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.game_clock import GameClockDisplay
from hoops_sim.tui.widgets.mini_box_score import MiniBoxScore
from hoops_sim.tui.widgets.momentum_bar import MomentumBar
from hoops_sim.tui.widgets.play_by_play import PlayByPlay
from hoops_sim.tui.widgets.scoreboard import Scoreboard
from hoops_sim.utils.rng import SeededRNG


class LiveGameScreen(Screen):
    """The main event: real-time play-by-play simulation.

    Runs the GameSimulator and renders game state in real time with
    play-by-play narration, live scoreboard, and mini box scores.
    """

    BINDINGS = [
        ("space", "toggle_pause", "Pause/Resume"),
        ("f", "fast_forward", "Fast"),
        ("s", "slow_down", "Slow"),
        ("i", "instant_sim", "Instant"),
        ("b", "toggle_box_score", "Box Score"),
        ("q", "end_game", "End Game"),
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

        # Simulation state
        self._paused = False
        self._tick_delay = 0.1  # seconds between ticks
        self._game_over = False
        self._sim_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]

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
            self._home_stats = TeamGameStats(
                team_id=0, team_name="Home",
            )
            self._away_stats = TeamGameStats(
                team_id=0, team_name="Away",
            )
            self._game_state = GameState()
            self._momentum = MomentumTracker()

    def compose(self) -> ComposeResult:
        home_name = self._home_team.full_name if self._home_team else "Home"
        away_name = self._away_team.full_name if self._away_team else "Away"

        yield Header()
        with Vertical(id="live-game"):
            # Top: clock + scoreboard
            with Horizontal(id="live-game-top"):
                yield GameClockDisplay(
                    quarter=self._game_state.clock.quarter,
                    game_clock=self._game_state.clock.display,
                    shot_clock=self._game_state.clock.shot_clock_display,
                    id="game-clock",
                )
                yield Scoreboard(
                    home_name=home_name,
                    away_name=away_name,
                    home_score=self._game_state.score.home,
                    away_score=self._game_state.score.away,
                    id="game-scoreboard",
                )

            # Middle: play-by-play + stats
            with Horizontal(id="live-game-middle"):
                with Vertical(id="live-game-play-by-play"):
                    yield PlayByPlay(id="game-pbp")
                with Vertical(id="live-game-stats"):
                    yield MiniBoxScore(
                        team_name=home_name,
                        player_stats=list(self._home_stats.player_stats.values()),
                        id="home-box",
                    )
                    yield MiniBoxScore(
                        team_name=away_name,
                        player_stats=list(self._away_stats.player_stats.values()),
                        id="away-box",
                    )

            # Bottom: momentum + controls
            with Horizontal(id="live-game-bottom"):
                yield MomentumBar(
                    value=self._momentum.value,
                    home_name=home_name[:8],
                    away_name=away_name[:8],
                    id="game-momentum",
                )
                yield Label(
                    " [Space] Pause  [F] Fast  [S] Slow  [I] Instant  [Q] End",
                    id="live-game-controls",
                )
        yield Footer()

    def on_mount(self) -> None:
        """Start the simulation loop."""
        pbp = self.query_one("#game-pbp", PlayByPlay)
        home_name = self._home_team.full_name if self._home_team else "Home"
        away_name = self._away_team.full_name if self._away_team else "Away"
        pbp.add_text(
            f"Welcome to {home_name} vs {away_name}!",
            NarrationIntensity.HIGH,
        )
        pbp.add_text("Tip-off!", NarrationIntensity.MEDIUM)

        self._sim_task = asyncio.ensure_future(self._run_simulation())

    async def _run_simulation(self) -> None:
        """Main simulation loop using the real GameSimulator."""
        if self._simulator is None:
            return

        while not self._game_over:
            if self._paused:
                await asyncio.sleep(0.05)
                continue

            # Step the simulator one tick
            events = self._simulator.step()

            # Process events for the UI
            for sim_event in events:
                self._handle_sim_event(sim_event)

            # Check if game ended
            if self._simulator.is_game_over:
                self._game_over = True
                break

            # Update UI
            self._refresh_widgets()

            if self._tick_delay > 0:
                await asyncio.sleep(self._tick_delay)

        self._on_game_end()

    def _handle_sim_event(self, sim_event: SimEvent) -> None:
        """Process a simulation event for the UI."""
        if sim_event.narration is None:
            return

        try:
            pbp = self.query_one("#game-pbp", PlayByPlay)
            pbp.add_event(sim_event.narration)
        except Exception:
            pass

    def _on_game_end(self) -> None:
        """Handle end of game."""
        try:
            pbp = self.query_one("#game-pbp", PlayByPlay)
            gs = self._game_state
            gs.phase = GamePhase.POST_GAME
            pbp.add_text(
                f"FINAL: {gs.score.away} - {gs.score.home}",
                NarrationIntensity.MAXIMUM,
            )
        except Exception:
            pass

        self._refresh_widgets()

        # Record game result if we have a scheduled game
        gs = self._game_state
        if self._scheduled_game and not self._scheduled_game.played:
            self._scheduled_game.record_result(gs.score.home, gs.score.away)

            if self._standings and self._home_team and self._away_team:
                same_conf = self._home_team.conference == self._away_team.conference
                same_div = self._home_team.division == self._away_team.division
                self._standings.record_game(
                    self._home_team.id, self._away_team.id,
                    gs.score.home, gs.score.away,
                    is_home_win=gs.score.home > gs.score.away,
                    is_conference=same_conf, is_division=same_div,
                )

    def _refresh_widgets(self) -> None:
        """Update all live game widgets."""
        gs = self._game_state

        try:
            clock = self.query_one("#game-clock", GameClockDisplay)
            clock.update_clock(
                quarter=gs.clock.quarter,
                game_clock=gs.clock.display,
                shot_clock=gs.clock.shot_clock_display,
                is_overtime=gs.clock.is_overtime,
            )
        except Exception:
            pass

        try:
            scoreboard = self.query_one("#game-scoreboard", Scoreboard)
            scoreboard.update_score(gs.score.home, gs.score.away)
        except Exception:
            pass

        try:
            momentum = self.query_one("#game-momentum", MomentumBar)
            momentum.update_momentum(self._momentum.value)
        except Exception:
            pass

        try:
            home_box = self.query_one("#home-box", MiniBoxScore)
            home_box.update_stats(list(self._home_stats.player_stats.values()))
        except Exception:
            pass

        try:
            away_box = self.query_one("#away-box", MiniBoxScore)
            away_box.update_stats(list(self._away_stats.player_stats.values()))
        except Exception:
            pass

    def action_toggle_pause(self) -> None:
        """Toggle pause/resume."""
        self._paused = not self._paused
        status = "PAUSED" if self._paused else "RESUMED"
        self.notify(status)

    def action_fast_forward(self) -> None:
        """Reduce tick delay for faster simulation."""
        self._tick_delay = max(0.01, self._tick_delay / 2)
        self.notify(f"Speed: {self._tick_delay:.3f}s/tick")

    def action_slow_down(self) -> None:
        """Increase tick delay for slower simulation."""
        self._tick_delay = min(0.5, self._tick_delay * 2)
        self.notify(f"Speed: {self._tick_delay:.3f}s/tick")

    def action_instant_sim(self) -> None:
        """Instant sim to end of game."""
        self._tick_delay = 0.0
        self.notify("Instant sim...")

    def action_toggle_box_score(self) -> None:
        """Toggle box score overlay."""
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
        self._game_over = True
        if self._sim_task:
            self._sim_task.cancel()

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
