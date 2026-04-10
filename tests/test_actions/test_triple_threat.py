"""Tests for triple threat mechanics."""

from __future__ import annotations

import pytest

from hoops_sim.actions.triple_threat import (
    TripleThreatAction,
    TripleThreatResult,
    resolve_triple_threat,
)
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestTripleThreat:
    def test_jab_step_returns_result(self, rng):
        result = resolve_triple_threat(
            action=TripleThreatAction.JAB_STEP,
            basketball_iq=80,
            ball_handle=75,
            defender_iq=60,
            defender_consistency=50,
            defender_distance=3.0,
            rng=rng,
        )
        assert isinstance(result, TripleThreatResult)
        assert result.action == TripleThreatAction.JAB_STEP
        assert result.time_cost_ticks == 4

    def test_pump_fake_returns_result(self, rng):
        result = resolve_triple_threat(
            action=TripleThreatAction.PUMP_FAKE,
            basketball_iq=85,
            ball_handle=70,
            defender_iq=50,
            defender_consistency=40,
            defender_distance=2.0,
            rng=rng,
        )
        assert isinstance(result, TripleThreatResult)
        assert result.action == TripleThreatAction.PUMP_FAKE
        assert result.time_cost_ticks == 5

    def test_direct_drive(self, rng):
        result = resolve_triple_threat(
            action=TripleThreatAction.DIRECT_DRIVE,
            basketball_iq=70,
            ball_handle=85,
            defender_iq=60,
            defender_consistency=50,
            defender_distance=4.0,
            rng=rng,
        )
        assert result.action == TripleThreatAction.DIRECT_DRIVE
        assert result.time_cost_ticks == 3
        assert result.separation_gained > 0

    def test_direct_shoot(self, rng):
        result = resolve_triple_threat(
            action=TripleThreatAction.DIRECT_SHOOT,
            basketball_iq=70,
            ball_handle=60,
            defender_iq=60,
            defender_consistency=50,
            defender_distance=5.0,
            rng=rng,
        )
        assert result.action == TripleThreatAction.DIRECT_SHOOT
        assert result.time_cost_ticks == 2
        assert result.separation_gained == 0.0

    def test_high_iq_pump_fake_more_effective(self):
        """High-IQ player should get more bites on pump fakes over many trials."""
        high_iq_bites = 0
        low_iq_bites = 0
        trials = 200

        for i in range(trials):
            rng = SeededRNG(seed=i)
            result = resolve_triple_threat(
                action=TripleThreatAction.PUMP_FAKE,
                basketball_iq=95, ball_handle=80,
                defender_iq=50, defender_consistency=40,
                defender_distance=2.0, rng=rng,
            )
            if result.defender_bit:
                high_iq_bites += 1

        for i in range(trials):
            rng = SeededRNG(seed=i + 1000)
            result = resolve_triple_threat(
                action=TripleThreatAction.PUMP_FAKE,
                basketball_iq=50, ball_handle=50,
                defender_iq=50, defender_consistency=40,
                defender_distance=2.0, rng=rng,
            )
            if result.defender_bit:
                low_iq_bites += 1

        assert high_iq_bites > low_iq_bites
