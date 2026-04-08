"""Tests for dribble move system."""

from __future__ import annotations

import pytest

from hoops_sim.actions.dribble import (
    DRIBBLE_MOVES,
    DribbleMoveType,
    resolve_dribble_move,
)
from hoops_sim.utils.rng import SeededRNG


class TestDribbleMoves:
    def test_all_move_types_defined(self):
        for mt in DribbleMoveType:
            assert mt in DRIBBLE_MOVES

    def test_successful_move(self):
        # Elite ball handler vs poor defender = likely success
        result = resolve_dribble_move(
            ball_handle=95, energy_pct=1.0, defender_lateral=40,
            defender_steal=30, move_type=DribbleMoveType.CROSSOVER,
            has_ankle_breaker_badge=False, badge_tier=0, rng=SeededRNG(42),
        )
        assert result.success
        assert result.separation > 0
        assert result.energy_cost > 0

    def test_failed_move(self):
        # Poor ball handler vs elite defender
        results = [
            resolve_dribble_move(
                ball_handle=30, energy_pct=0.5, defender_lateral=95,
                defender_steal=90, move_type=DribbleMoveType.SPIN_MOVE,
                has_ankle_breaker_badge=False, badge_tier=0, rng=SeededRNG(seed),
            )
            for seed in range(50)
        ]
        failures = sum(1 for r in results if not r.success)
        assert failures > 20  # Most should fail

    def test_ankle_breaker(self):
        # Elite handler with badge, run many times
        ankle_breakers = 0
        for seed in range(200):
            result = resolve_dribble_move(
                ball_handle=98, energy_pct=1.0, defender_lateral=50,
                defender_steal=40, move_type=DribbleMoveType.CROSSOVER,
                has_ankle_breaker_badge=True, badge_tier=4, rng=SeededRNG(seed),
            )
            if result.ankle_breaker:
                ankle_breakers += 1
        assert ankle_breakers > 0  # Should get at least some

    def test_turnover_possible(self):
        turnovers = 0
        for seed in range(200):
            result = resolve_dribble_move(
                ball_handle=40, energy_pct=0.5, defender_lateral=90,
                defender_steal=95, move_type=DribbleMoveType.SPIN_MOVE,
                has_ankle_breaker_badge=False, badge_tier=0, rng=SeededRNG(seed),
            )
            if result.turnover:
                turnovers += 1
        assert turnovers > 0

    def test_step_back_no_speed_boost(self):
        spec = DRIBBLE_MOVES[DribbleMoveType.STEP_BACK]
        assert spec.speed_boost == 0.0
        assert spec.space_created > 0

    def test_fatigue_reduces_success(self):
        fresh_successes = sum(
            1 for seed in range(100)
            if resolve_dribble_move(
                ball_handle=70, energy_pct=1.0, defender_lateral=70,
                defender_steal=50, move_type=DribbleMoveType.CROSSOVER,
                has_ankle_breaker_badge=False, badge_tier=0, rng=SeededRNG(seed),
            ).success
        )
        tired_successes = sum(
            1 for seed in range(100)
            if resolve_dribble_move(
                ball_handle=70, energy_pct=0.3, defender_lateral=70,
                defender_steal=50, move_type=DribbleMoveType.CROSSOVER,
                has_ankle_breaker_badge=False, badge_tier=0, rng=SeededRNG(seed),
            ).success
        )
        assert fresh_successes >= tired_successes
