"""Tests for closeout mechanics."""

from __future__ import annotations

import pytest

from hoops_sim.defense.closeout import (
    CloseoutResult,
    CloseoutType,
    evaluate_closeout,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestCloseout:
    def test_no_closeout_when_too_far(self, rng):
        result = evaluate_closeout(
            defender_position=Vec2(20.0, 25.0),
            shooter_position=Vec2(70.0, 10.0),
            defender_speed=70,
            defender_lateral=65,
            closeout_aggression=0.5,
            time_available_ticks=5,
            rng=rng,
        )
        assert result.closeout_type in (CloseoutType.NO_CLOSEOUT, CloseoutType.LATE)

    def test_hard_closeout_with_aggressive_defender(self, rng):
        result = evaluate_closeout(
            defender_position=Vec2(68.0, 11.0),
            shooter_position=Vec2(70.0, 10.0),
            defender_speed=80,
            defender_lateral=75,
            closeout_aggression=0.8,
            time_available_ticks=10,
            rng=rng,
        )
        assert result.closeout_type == CloseoutType.HARD
        assert result.contest_quality > 0.5

    def test_controlled_closeout(self, rng):
        result = evaluate_closeout(
            defender_position=Vec2(67.0, 11.0),
            shooter_position=Vec2(70.0, 10.0),
            defender_speed=75,
            defender_lateral=70,
            closeout_aggression=0.2,
            time_available_ticks=10,
            rng=rng,
        )
        assert result.closeout_type == CloseoutType.CONTROLLED
        assert result.can_be_pump_faked is False

    def test_hard_closeout_can_be_pump_faked(self):
        """Hard closeouts should sometimes be vulnerable to pump fakes."""
        pump_faked = 0
        for i in range(100):
            r = SeededRNG(seed=i)
            result = evaluate_closeout(
                defender_position=Vec2(68.0, 11.0),
                shooter_position=Vec2(70.0, 10.0),
                defender_speed=80, defender_lateral=70,
                closeout_aggression=0.9,
                time_available_ticks=10, rng=r,
            )
            if result.can_be_pump_faked:
                pump_faked += 1
        assert pump_faked > 10  # Should happen sometimes

    def test_contest_quality_range(self, rng):
        result = evaluate_closeout(
            defender_position=Vec2(69.0, 10.5),
            shooter_position=Vec2(70.0, 10.0),
            defender_speed=80, defender_lateral=75,
            closeout_aggression=0.5,
            time_available_ticks=15, rng=rng,
        )
        assert 0.0 <= result.contest_quality <= 1.0
