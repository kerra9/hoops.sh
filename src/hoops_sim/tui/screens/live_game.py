"""Live Game screen -- real-time play-by-play simulation.

Broadcast-style layout with court map, enhanced play-by-play,
broadcast scoreboard, context strip, and mini box scores.
Powered by the real GameSimulator with Rich-only rendering.
"""

from __future__ import annotations

import time
from typing import Optional

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
from hoops_sim.tui.base import Screen, console
from hoops_sim.tui.widgets.broadcast_scoreboard import BroadcastScoreboard
from hoops_sim.tui.widgets.context_strip import ContextStrip
from hoops_sim.tui.widgets.court_map import CourtMap
from hoops_sim.tui.widgets.mini_box_score import MiniBoxScore
from hoops_sim.tui.widgets.play_by_play import PlayByPlay
from hoops_sim.utils.rng import SeededRNG


class LiveGameScreen(Screen):
    """The main event: real-time play-by-play simulation."""

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
        self._tick_delay = 0.1
        self._game_over = False
        self._tick_count = 0

        # Widgets
        self._scoreboard = BroadcastScoreboard(
            home_name=home_team.full_name if home_team else "Home",
            away_name=away_team.full_name if away_team else "Away",
            home_abbr=home_team.abbreviation if home_team else "HME",
            away_abbr=away_team.abbreviation if away_team else "AWY",
        )
        self._court = CourtMap()
        self._pbp = PlayByPlay()
        self._context = ContextStrip(
            home_name=home_team.full_name if home_team else "Home",
            away_name=away_team.full_name if away_team else "Away",
        )

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

    def render(self) -> str:
        """Render the live game display."""
        lines = [self._scoreboard.render(), ""]
        lines.append(self._court.render())
        lines.append("")
        lines.append(self._pbp.render())
        lines.append("")
        lines.append(self._context.render())
        lines.append("")
        lines.append(
            " [Space] Pause  [F] Fast  [S] Slow  [I] Instant  [B] Box  [Q] End"
        )
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        """In Rich-only mode the game runs synchronously via run_game()."""
        c = choice.strip().lower()
        if c == "q":
            self.action_end_game()
        elif c == "b":
            self.action_toggle_box_score()
        elif c == "i":
            self._tick_delay = 0.0
            self._run_game()

    def run_game(self) -> None:
        """Run the full game simulation synchronously."""
        if self._simulator is None:
            return

        home_name = self._home_team.full_name if self._home_team else "Home"
        away_name = self._away_team.full_name if self._away_team else "Away"
        self._pbp.add_text(
            f"Welcome to {home_name} vs {away_name}!",
            NarrationIntensity.HIGH,
        )
        self._pbp.add_text("Tip-off!", NarrationIntensity.MEDIUM)

        while not self._game_over:
            events = self._simulator.step()
            self._tick_count += 1

            for sim_event in events:
                if sim_event.narration:
                    self._pbp.add_event(sim_event.narration)

            if self._simulator.is_game_over:
                self._game_over = True
                break

            self._refresh_widgets()

            if self._tick_delay > 0 and self._tick_count % 50 == 0:
                console.clear()
                console.print(self.render())

        self._on_game_end()
        console.clear()
        console.print(self.render())

    def _run_game(self) -> None:
        """Alias for run_game used by instant sim."""
        self.run_game()

    def _refresh_widgets(self) -> None:
        """Update all live game widgets."""
        gs = self._game_state

        self._scoreboard.update_state(
            home_score=gs.score.home,
            away_score=gs.score.away,
            quarter=gs.clock.quarter,
            game_clock=gs.clock.display,
            shot_clock=gs.clock.shot_clock_display,
            is_overtime=gs.clock.is_overtime,
        )

        self._context.update_context(momentum=self._momentum.value)

        if hasattr(gs, "court_state") and gs.court_state is not None:
            cs = gs.court_state
            offense = [(p.position.x, p.position.y) for p in cs.offensive_players]
            defense = [(p.position.x, p.position.y) for p in cs.defensive_players]
            self._court.update_positions(
                offense=offense,
                defense=defense,
                ball_carrier=cs.ball_handler_index,
            )

    def _on_game_end(self) -> None:
        """Handle end of game."""
        gs = self._game_state
        gs.phase = GamePhase.POST_GAME
        self._pbp.add_text(
            f"FINAL: {gs.score.away} - {gs.score.home}",
            NarrationIntensity.MAXIMUM,
        )

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
        self._game_over = True

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
