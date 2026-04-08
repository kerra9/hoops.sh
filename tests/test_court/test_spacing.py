"""Tests for spacing calculator."""

from __future__ import annotations

import pytest

from hoops_sim.court.spacing import average_spacing, spacing_quality
from hoops_sim.physics.vec import Vec2


class TestAverageSpacing:
    def test_empty(self):
        assert average_spacing([]) == 0.0

    def test_single_player(self):
        assert average_spacing([Vec2(0, 0)]) == 0.0

    def test_two_players(self):
        positions = [Vec2(0, 0), Vec2(10, 0)]
        assert average_spacing(positions) == pytest.approx(10.0)

    def test_bunched_up(self):
        positions = [Vec2(10, 10), Vec2(11, 10), Vec2(10, 11), Vec2(11, 11)]
        assert average_spacing(positions) < 3.0

    def test_spread_out(self):
        positions = [Vec2(0, 0), Vec2(20, 0), Vec2(0, 20), Vec2(20, 20)]
        assert average_spacing(positions) > 15.0


class TestSpacingQuality:
    def test_good_spacing(self):
        basket = Vec2(88.75, 25.0)
        positions = [
            Vec2(65, 25),  # Top of key
            Vec2(68, 5),   # Right corner
            Vec2(68, 45),  # Left corner
            Vec2(75, 15),  # Right wing
            Vec2(75, 35),  # Left wing
        ]
        quality = spacing_quality(positions, basket)
        assert quality > 0.4

    def test_bunched_spacing(self):
        basket = Vec2(88.75, 25.0)
        positions = [
            Vec2(85, 24),
            Vec2(85, 25),
            Vec2(85, 26),
            Vec2(86, 24),
            Vec2(86, 26),
        ]
        quality = spacing_quality(positions, basket)
        assert quality < 0.5

    def test_single_player(self):
        quality = spacing_quality([Vec2(50, 25)], Vec2(88.75, 25))
        assert quality == pytest.approx(0.5)
