"""Tests for situational basketball and clock management."""

from __future__ import annotations

import pytest

from hoops_sim.engine.situational import (
    SituationalModifiers,
    SituationType,
    evaluate_situation,
)


class TestSituational:
    def test_normal_situation(self):
        sit_type, mods = evaluate_situation(
            game_clock=500.0, shot_clock=20.0,
            quarter=2, score_diff=5, is_home=True,
        )
        assert sit_type == SituationType.NORMAL

    def test_heave_under_3_seconds(self):
        sit_type, mods = evaluate_situation(
            game_clock=2.0, shot_clock=2.0,
            quarter=4, score_diff=-3, is_home=False,
        )
        assert sit_type == SituationType.HEAVE
        assert mods.shot_volume_mod > 1.5

    def test_last_shot(self):
        sit_type, mods = evaluate_situation(
            game_clock=6.0, shot_clock=6.0,
            quarter=4, score_diff=0, is_home=True,
        )
        assert sit_type == SituationType.LAST_SHOT
        assert mods.iso_tendency_mod > 1.0

    def test_two_for_one(self):
        sit_type, mods = evaluate_situation(
            game_clock=34.0, shot_clock=24.0,
            quarter=2, score_diff=2, is_home=True,
        )
        assert sit_type == SituationType.TWO_FOR_ONE
        assert mods.pace_mod > 1.0

    def test_clutch_time(self):
        sit_type, mods = evaluate_situation(
            game_clock=180.0, shot_clock=24.0,
            quarter=4, score_diff=-2, is_home=True,
        )
        assert sit_type == SituationType.CLUTCH
        assert mods.defensive_intensity_mod > 1.0
        assert mods.gambling_mod < 1.0  # Less gambling

    def test_milk_clock(self):
        sit_type, mods = evaluate_situation(
            game_clock=90.0, shot_clock=24.0,
            quarter=4, score_diff=8, is_home=True,
        )
        assert sit_type == SituationType.MILK_CLOCK
        assert mods.pace_mod < 1.0

    def test_hurry_up(self):
        sit_type, mods = evaluate_situation(
            game_clock=90.0, shot_clock=24.0,
            quarter=4, score_diff=-8, is_home=True,
        )
        assert sit_type == SituationType.HURRY_UP
        assert mods.pace_mod > 1.0
        assert mods.three_point_tendency_mod > 1.0

    def test_garbage_time(self):
        sit_type, mods = evaluate_situation(
            game_clock=300.0, shot_clock=24.0,
            quarter=4, score_diff=30, is_home=True,
        )
        assert sit_type == SituationType.GARBAGE_TIME
        assert mods.defensive_intensity_mod < 1.0

    def test_intentional_foul(self):
        sit_type, mods = evaluate_situation(
            game_clock=20.0, shot_clock=20.0,
            quarter=4, score_diff=-8, is_home=True,
        )
        assert sit_type == SituationType.INTENTIONAL_FOUL
