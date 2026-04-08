"""Tests for possession state machine."""

from __future__ import annotations

import pytest

from hoops_sim.engine.possession import PossessionResult, PossessionState, PossessionTracker


class TestPossessionTracker:
    def test_initial_state(self):
        pt = PossessionTracker()
        assert pt.state == PossessionState.PRE_INBOUND
        assert pt.is_dead()

    def test_new_possession(self):
        pt = PossessionTracker()
        pt.new_possession(1, 2)
        assert pt.offensive_team_id == 1
        assert pt.defensive_team_id == 2
        assert pt.possession_number == 1
        assert pt.state == PossessionState.PRE_INBOUND

    def test_transition(self):
        pt = PossessionTracker()
        pt.transition_to(PossessionState.LIVE)
        assert pt.state == PossessionState.LIVE
        assert pt.ticks_in_state == 0
        assert pt.is_live()

    def test_tick(self):
        pt = PossessionTracker()
        pt.transition_to(PossessionState.LIVE)
        pt.tick()
        pt.tick()
        assert pt.ticks_in_state == 2
        assert pt.ticks_total == 2

    def test_end_possession(self):
        pt = PossessionTracker()
        pt.transition_to(PossessionState.LIVE)
        pt.end_possession(PossessionResult.MADE_TWO)
        assert pt.result == PossessionResult.MADE_TWO
        assert pt.state == PossessionState.DEAD_BALL

    def test_is_live(self):
        pt = PossessionTracker()
        pt.transition_to(PossessionState.LIVE)
        assert pt.is_live()
        pt.transition_to(PossessionState.TRANSITION)
        assert pt.is_live()
        pt.transition_to(PossessionState.SHOT_IN_AIR)
        assert pt.is_live()

    def test_is_dead(self):
        pt = PossessionTracker()
        assert pt.is_dead()
        pt.transition_to(PossessionState.DEAD_BALL)
        assert pt.is_dead()
        pt.transition_to(PossessionState.TIMEOUT)
        assert pt.is_dead()

    def test_seconds_elapsed(self):
        pt = PossessionTracker()
        pt.transition_to(PossessionState.LIVE)
        for _ in range(50):
            pt.tick()
        assert pt.seconds_elapsed() == pytest.approx(5.0)

    def test_multiple_possessions(self):
        pt = PossessionTracker()
        pt.new_possession(1, 2)
        pt.transition_to(PossessionState.LIVE)
        pt.end_possession(PossessionResult.MADE_TWO)

        pt.new_possession(2, 1)
        assert pt.possession_number == 2
        assert pt.offensive_team_id == 2
        assert pt.result is None
