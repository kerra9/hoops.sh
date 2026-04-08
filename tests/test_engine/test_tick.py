"""Tests for the tick engine."""

from __future__ import annotations

import pytest

from hoops_sim.engine.clock import GameClock
from hoops_sim.engine.game import GamePhase, GameScore, GameState
from hoops_sim.engine.possession import PossessionState, PossessionTracker
from hoops_sim.engine.tick import TickEngine, TickEventType
from hoops_sim.models.team import Team


class TestTickEngine:
    def _make_game_state(self) -> GameState:
        gs = GameState(
            home_team=Team(id=1, city="Home", name="Team"),
            away_team=Team(id=2, city="Away", name="Team"),
        )
        gs.start_quarter(1)
        gs.clock.start()
        gs.possession.new_possession(1, 2)
        gs.possession.transition_to(PossessionState.LIVE)
        return gs

    def test_tick_advances_clock(self):
        gs = self._make_game_state()
        engine = TickEngine(gs)
        initial_clock = gs.clock.game_clock
        engine.process_tick()
        assert gs.clock.game_clock < initial_clock

    def test_tick_increments_counter(self):
        gs = self._make_game_state()
        engine = TickEngine(gs)
        engine.process_tick()
        assert engine.tick_number == 1
        engine.process_tick()
        assert engine.tick_number == 2

    def test_clock_stops_on_dead_ball(self):
        gs = self._make_game_state()
        gs.possession.transition_to(PossessionState.DEAD_BALL)
        engine = TickEngine(gs)
        initial = gs.clock.game_clock
        engine.process_tick()
        # Clock should not advance when possession is dead
        assert gs.clock.game_clock == initial

    def test_shot_clock_violation(self):
        gs = self._make_game_state()
        gs.clock.shot_clock = 0.05  # About to expire
        engine = TickEngine(gs)
        result = engine.process_tick()
        # Shot clock should expire
        assert any(e.event_type == TickEventType.SHOT_CLOCK_VIOLATION for e in result.events)

    def test_quarter_end(self):
        gs = self._make_game_state()
        gs.clock.game_clock = 0.05  # About to end
        gs.clock.shot_clock = 10.0  # Shot clock has time, only game clock expires
        engine = TickEngine(gs)
        result = engine.process_tick()
        assert any(e.event_type == TickEventType.QUARTER_END for e in result.events)

    def test_run_multiple_ticks(self):
        gs = self._make_game_state()
        engine = TickEngine(gs)
        results = engine.run_ticks(100)
        assert len(results) == 100
        assert engine.tick_number == 100

    def test_possession_tick_advances(self):
        gs = self._make_game_state()
        engine = TickEngine(gs)
        engine.process_tick()
        assert gs.possession.ticks_in_state == 1


class TestGameScore:
    def test_initial(self):
        score = GameScore()
        assert score.home == 0
        assert score.away == 0
        assert score.diff == 0

    def test_add_points(self):
        score = GameScore()
        score.add_points(is_home=True, points=3, quarter=1)
        assert score.home == 3
        assert score.quarter_scores_home[0] == 3

    def test_diff(self):
        score = GameScore()
        score.add_points(True, 10, 1)
        score.add_points(False, 7, 1)
        assert score.diff == 3

    def test_overtime_quarters(self):
        score = GameScore()
        score.add_points(True, 5, 5)  # OT
        assert len(score.quarter_scores_home) == 5


class TestGameState:
    def test_start_quarter(self):
        gs = GameState(
            home_team=Team(id=1),
            away_team=Team(id=2),
        )
        gs.start_quarter(1)
        assert gs.phase == GamePhase.QUARTER
        assert gs.home_team_fouls == 0

    def test_overtime(self):
        gs = GameState(home_team=Team(id=1), away_team=Team(id=2))
        gs.start_quarter(5)
        assert gs.phase == GamePhase.OVERTIME

    def test_is_in_bonus(self):
        gs = GameState(home_team=Team(id=1), away_team=Team(id=2))
        gs.possession.offensive_team_id = 1
        gs.away_team_fouls = 5
        assert gs.is_in_bonus(team_on_offense=True)

    def test_is_tied(self):
        gs = GameState()
        assert gs.is_tied()
        gs.score.home = 10
        assert not gs.is_tied()
