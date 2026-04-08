"""Tests for PlayerBody model."""

from __future__ import annotations

import pytest

from hoops_sim.models.body import Handedness, HandSize, PlayerBody


class TestPlayerBody:
    def test_defaults(self):
        body = PlayerBody()
        assert body.height_inches == 78
        assert body.weight_lbs == 210
        assert body.handedness == Handedness.RIGHT

    def test_height_feet(self):
        body = PlayerBody(height_inches=78)
        assert body.height_feet == pytest.approx(6.5)

    def test_height_display(self):
        body = PlayerBody(height_inches=78)
        assert body.height_display == "6'6\""

        body2 = PlayerBody(height_inches=84)
        assert body2.height_display == "7'0\""

    def test_wingspan_ratio(self):
        body = PlayerBody(height_inches=78, wingspan_inches=84)
        assert body.wingspan_to_height_ratio > 1.0

        body2 = PlayerBody(height_inches=78, wingspan_inches=78)
        assert body2.wingspan_to_height_ratio == pytest.approx(1.0)

    def test_bmi(self):
        body = PlayerBody(height_inches=78, weight_lbs=210)
        bmi = body.bmi
        assert 20 < bmi < 30

    def test_is_long_for_height(self):
        long = PlayerBody(height_inches=78, wingspan_inches=84)
        assert long.is_long_for_height()

        normal = PlayerBody(height_inches=78, wingspan_inches=80)
        assert not normal.is_long_for_height()

    def test_is_undersized(self):
        body = PlayerBody(height_inches=72)
        assert body.is_undersized_for_position(75)
        assert not body.is_undersized_for_position(72)

    def test_strength_modifier(self):
        light = PlayerBody(weight_lbs=180)
        heavy = PlayerBody(weight_lbs=260)
        assert light.strength_modifier() < 1.0
        assert heavy.strength_modifier() > 1.0


class TestHandedness:
    def test_values(self):
        assert Handedness.RIGHT.value == "right"
        assert Handedness.LEFT.value == "left"
        assert Handedness.AMBIDEXTROUS.value == "ambidextrous"


class TestHandSize:
    def test_values(self):
        assert len(HandSize) == 4
