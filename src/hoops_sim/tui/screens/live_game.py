"""Live Game screen -- real-time play-by-play simulation."""

from __future__ import annotations

import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.tick import TickEngine, TickEventType
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

    Runs the TickEngine and renders game state in real time with
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

        # Initialize game state
        self._game_state = GameState(
            home_team=home_team,
            away_team=away_team,
        )
        self._tick_engine = TickEngine(self._game_state)
        self._rng = SeededRNG(seed=seed)
        self._narration = NarrationEngine(self._rng)
        self._momentum = MomentumTracker()

        # Stats tracking
        self._home_stats = TeamGameStats(
            team_id=home_team.id if home_team else 0,
            team_name=home_team.full_name if home_team else "Home",
        )
        self._away_stats = TeamGameStats(
            team_id=away_team.id if away_team else 0,
            team_name=away_team.full_name if away_team else "Away",
        )

        # Initialize player stats for all roster players
        if home_team:
            for p in home_team.roster:
                self._home_stats.add_player(p.id, p.full_name)
        if away_team:
            for p in away_team.roster:
                self._away_stats.add_player(p.id, p.full_name)

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
        from hoops_sim.engine.possession import PossessionState

        self._game_state.phase = GamePhase.QUARTER
        self._game_state.clock.start()
        # Transition possession to LIVE so the tick engine advances the clock
        self._game_state.possession.transition_to(PossessionState.LIVE)
        if self._home_team:
            self._game_state.possession.offensive_team_id = self._home_team.id
        if self._away_team:
            self._game_state.possession.defensive_team_id = self._away_team.id

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
        """Main simulation loop running as an async task."""
        quarters_played = 0
        ticks_in_quarter = 0
        max_ticks_per_quarter = 7200  # 12 min * 60 sec / 0.1s

        while not self._game_over:
            if self._paused:
                await asyncio.sleep(0.05)
                continue

            # Process one tick
            result = self._tick_engine.process_tick()
            ticks_in_quarter += 1

            # Simulate game events probabilistically
            self._simulate_events(ticks_in_quarter)

            # Process tick events
            for event in result.events:
                if event.event_type == TickEventType.QUARTER_END:
                    quarters_played += 1
                    self._on_quarter_end(quarters_played)
                    ticks_in_quarter = 0
                    if quarters_played >= 4 and self._game_state.score.home != self._game_state.score.away:
                        self._game_over = True
                        break
                    # Start next quarter
                    self._game_state.clock.start_quarter(quarters_played + 1)
                    self._game_state.clock.start()
                elif event.event_type == TickEventType.SHOT_CLOCK_VIOLATION:
                    self._on_shot_clock_violation()

            if self._game_over:
                break

            # Update UI
            self._refresh_widgets()

            await asyncio.sleep(self._tick_delay)

        self._on_game_end()

    def _simulate_events(self, tick_num: int) -> None:
        """Simulate basketball events based on tick timing."""
        # Approximately every 40-60 ticks (~4-6 seconds), something happens
        if tick_num % 50 != 0 and self._rng.random() > 0.02:
            return

        gs = self._game_state
        is_home = self._rng.random() < 0.5
        team = self._home_team if is_home else self._away_team
        if not team or not team.roster:
            return

        # Pick a random player from starters
        starters = team.get_starters()
        if not starters:
            return
        player = self._rng.choice(starters)
        stats_tracker = self._home_stats if is_home else self._away_stats
        player_stats = stats_tracker.get_player(player.id)

        # Roll for event type
        roll = self._rng.random()
        pbp = self.query_one("#game-pbp", PlayByPlay)

        if roll < 0.45:  # Made shot
            is_three = self._rng.random() < 0.35
            points = 3 if is_three else 2
            player_stats.record_made_shot(is_three=is_three)
            gs.score.add_points(is_home, points, gs.clock.quarter)

            if is_home:
                self._momentum.on_home_score(points)
            else:
                self._momentum.on_away_score(points)

            event = self._narration.narrate_made_shot(
                shooter=player.full_name,
                team=team.full_name,
                points=points,
                distance=self._rng.uniform(3, 28),
                zone="mid-range" if not is_three else "three-point",
                lead=gs.score.diff if is_home else -gs.score.diff,
            )
            pbp.add_event(event)
            gs.clock.reset_shot_clock()

        elif roll < 0.75:  # Missed shot
            is_three = self._rng.random() < 0.35
            player_stats.record_missed_shot(is_three=is_three)
            event = self._narration.narrate_missed_shot(
                shooter=player.full_name,
                distance=self._rng.uniform(3, 28),
                zone="mid-range" if not is_three else "three-point",
            )
            pbp.add_event(event)
            gs.clock.reset_shot_clock()

        elif roll < 0.85:  # Turnover
            player_stats.turnovers += 1
            self._momentum.on_turnover(is_home)
            event = self._narration.narrate_turnover(
                player=player.full_name, team=team.full_name,
            )
            pbp.add_event(event)
            gs.clock.reset_shot_clock()

        elif roll < 0.92:  # Assist + made shot
            if len(starters) > 1:
                passer = self._rng.choice([s for s in starters if s.id != player.id])
                passer_stats = stats_tracker.get_player(passer.id)
                passer_stats.assists += 1
            is_three = self._rng.random() < 0.3
            points = 3 if is_three else 2
            player_stats.record_made_shot(is_three=is_three)
            gs.score.add_points(is_home, points, gs.clock.quarter)
            if is_home:
                self._momentum.on_home_score(points)
            else:
                self._momentum.on_away_score(points)

            event = self._narration.narrate_made_shot(
                shooter=player.full_name,
                team=team.full_name,
                points=points,
                distance=self._rng.uniform(3, 28),
                zone="paint" if not is_three else "corner",
                lead=gs.score.diff if is_home else -gs.score.diff,
            )
            pbp.add_event(event)
            gs.clock.reset_shot_clock()

        elif roll < 0.96:  # Rebound
            if self._rng.random() < 0.7:
                player_stats.defensive_rebounds += 1
            else:
                player_stats.offensive_rebounds += 1

        else:  # Free throws
            ft_count = self._rng.choice([1, 2, 2, 2, 3])
            for _ in range(ft_count):
                if self._rng.random() < 0.75:
                    player_stats.record_made_ft()
                    gs.score.add_points(is_home, 1, gs.clock.quarter)
                else:
                    player_stats.record_missed_ft()

        self._momentum.decay()

    def _on_quarter_end(self, quarter: int) -> None:
        """Handle end of quarter."""
        pbp = self.query_one("#game-pbp", PlayByPlay)
        gs = self._game_state
        q_name = f"Q{quarter}" if quarter <= 4 else f"OT{quarter - 4}"
        pbp.add_text(
            f"End of {q_name}. Score: {gs.score.away} - {gs.score.home}",
            NarrationIntensity.HIGH,
        )

    def _on_shot_clock_violation(self) -> None:
        """Handle shot clock violation."""
        pbp = self.query_one("#game-pbp", PlayByPlay)
        pbp.add_text("Shot clock violation!", NarrationIntensity.MEDIUM)
        self._game_state.clock.reset_shot_clock()
        self._game_state.clock.start()

    def _on_game_end(self) -> None:
        """Handle end of game."""
        pbp = self.query_one("#game-pbp", PlayByPlay)
        gs = self._game_state
        gs.phase = GamePhase.POST_GAME
        pbp.add_text(
            f"FINAL: {gs.score.away} - {gs.score.home}",
            NarrationIntensity.MAXIMUM,
        )
        self._refresh_widgets()

        # Record game result if we have a scheduled game
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
