"""Tests for rim interaction physics."""

from __future__ import annotations

import pytest

from hoops_sim.physics.rim_interaction import (
    CaromResult,
    ShotOutcome,
    calculate_carom_direction,
    calculate_entry_offset,
    resolve_rim_interaction,
)
from hoops_sim.physics.vec import Vec3
from hoops_sim.utils.constants import BASKET_HEIGHT, BASKET_X, BASKET_Y
from hoops_sim.utils.rng import SeededRNG


class TestEntryOffset:
    def test_dead_center(self):
        """Ball directly over basket center should have ~0 offset."""
        ball_pos = Vec3(BASKET_X, BASKET_Y, BASKET_HEIGHT)
        ball_vel = Vec3(0.0, 0.0, -5.0)
        offset = calculate_entry_offset(ball_pos, ball_vel)
        assert offset == pytest.approx(0.0, abs=0.1)

    def test_offset_increases_with_distance(self):
        """Ball further from center should have larger offset."""
        center = Vec3(BASKET_X, BASKET_Y, BASKET_HEIGHT)
        off_center = Vec3(BASKET_X + 0.3, BASKET_Y, BASKET_HEIGHT)
        vel = Vec3(0.0, 0.0, -5.0)

        offset_center = calculate_entry_offset(center, vel)
        offset_off = calculate_entry_offset(off_center, vel)
        assert offset_off > offset_center


class TestCaromDirection:
    def test_carom_has_reasonable_distance(self):
        rng = SeededRNG(seed=42)
        ball_pos = Vec3(BASKET_X + 0.3, BASKET_Y, BASKET_HEIGHT)
        spin = Vec3(150.0, 0.0, 0.0)

        carom = calculate_carom_direction(ball_pos, 30.0, spin, rng)
        assert carom.distance_ft > 0
        assert 0 <= carom.angle < 360

    def test_backspin_reduces_distance(self):
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=42)
        ball_pos = Vec3(BASKET_X + 0.3, BASKET_Y, BASKET_HEIGHT)

        no_spin = Vec3(0.0, 0.0, 0.0)
        high_spin = Vec3(300.0, 0.0, 0.0)

        carom_no_spin = calculate_carom_direction(ball_pos, 30.0, no_spin, rng1)
        carom_high_spin = calculate_carom_direction(ball_pos, 30.0, high_spin, rng2)

        assert carom_high_spin.distance_ft < carom_no_spin.distance_ft


class TestResolveRimInteraction:
    def test_swish_on_center_shot(self):
        """Dead-center shot should be a swish."""
        rng = SeededRNG(seed=42)
        ball_pos = Vec3(BASKET_X, BASKET_Y, BASKET_HEIGHT)
        ball_vel = Vec3(0.0, 0.0, -5.0)
        spin = Vec3(180.0, 0.0, 0.0)

        result = resolve_rim_interaction(ball_pos, ball_vel, spin, rng)
        assert result.outcome == ShotOutcome.SWISH
        assert result.made is True
        assert result.carom is None

    def test_airball_on_far_miss(self):
        """Shot way off target should be an airball."""
        rng = SeededRNG(seed=42)
        ball_pos = Vec3(BASKET_X + 2.0, BASKET_Y + 2.0, BASKET_HEIGHT)
        ball_vel = Vec3(5.0, 5.0, -3.0)
        spin = Vec3(100.0, 0.0, 0.0)

        result = resolve_rim_interaction(ball_pos, ball_vel, spin, rng)
        assert result.outcome == ShotOutcome.AIRBALL
        assert result.made is False
        assert result.carom is not None

    def test_miss_has_carom(self):
        """Missed shots should have carom information."""
        rng = SeededRNG(seed=42)
        ball_pos = Vec3(BASKET_X + 0.4, BASKET_Y, BASKET_HEIGHT)
        ball_vel = Vec3(2.0, 0.0, -8.0)
        spin = Vec3(50.0, 0.0, 0.0)

        result = resolve_rim_interaction(ball_pos, ball_vel, spin, rng)
        if not result.made:
            assert result.carom is not None
            assert result.carom.distance_ft > 0

    def test_deterministic_with_seed(self):
        """Same seed should produce same result."""
        ball_pos = Vec3(BASKET_X + 0.25, BASKET_Y + 0.1, BASKET_HEIGHT)
        ball_vel = Vec3(1.0, 0.5, -6.0)
        spin = Vec3(160.0, 10.0, 0.0)

        r1 = resolve_rim_interaction(ball_pos, ball_vel, spin, SeededRNG(seed=77))
        r2 = resolve_rim_interaction(ball_pos, ball_vel, spin, SeededRNG(seed=77))

        assert r1.outcome == r2.outcome
        assert r1.made == r2.made
