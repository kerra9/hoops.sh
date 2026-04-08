"""Tests for passing system."""

from __future__ import annotations

import pytest

from hoops_sim.actions.passing import PassType, resolve_pass
from hoops_sim.utils.rng import SeededRNG


class TestResolvePassing:
    def test_easy_pass_completes(self):
        # Short, open, chest pass with good passer
        completed = sum(
            1 for seed in range(100)
            if resolve_pass(
                pass_accuracy=90, pass_vision=85, receiver_hands=80,
                pass_type=PassType.CHEST, distance=10.0, lane_quality=1.0,
                is_under_pressure=False, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).completed
        )
        assert completed > 80  # Most should complete

    def test_difficult_pass_fails_more(self):
        easy = sum(
            1 for seed in range(100)
            if resolve_pass(
                pass_accuracy=80, pass_vision=80, receiver_hands=80,
                pass_type=PassType.CHEST, distance=10.0, lane_quality=0.9,
                is_under_pressure=False, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).completed
        )
        hard = sum(
            1 for seed in range(100)
            if resolve_pass(
                pass_accuracy=80, pass_vision=80, receiver_hands=80,
                pass_type=PassType.NO_LOOK, distance=30.0, lane_quality=0.3,
                is_under_pressure=True, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).completed
        )
        assert easy > hard

    def test_pressure_reduces_completion(self):
        no_pressure = sum(
            1 for seed in range(100)
            if resolve_pass(
                pass_accuracy=70, pass_vision=70, receiver_hands=70,
                pass_type=PassType.CHEST, distance=15.0, lane_quality=0.7,
                is_under_pressure=False, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).completed
        )
        pressure = sum(
            1 for seed in range(100)
            if resolve_pass(
                pass_accuracy=70, pass_vision=70, receiver_hands=70,
                pass_type=PassType.CHEST, distance=15.0, lane_quality=0.7,
                is_under_pressure=True, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).completed
        )
        assert no_pressure >= pressure

    def test_interceptions_on_bad_lanes(self):
        interceptions = sum(
            1 for seed in range(200)
            if resolve_pass(
                pass_accuracy=60, pass_vision=50, receiver_hands=70,
                pass_type=PassType.CHEST, distance=20.0, lane_quality=0.2,
                is_under_pressure=True, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(seed),
            ).intercepted
        )
        assert interceptions > 0

    def test_all_pass_types(self):
        for pt in PassType:
            result = resolve_pass(
                pass_accuracy=75, pass_vision=75, receiver_hands=75,
                pass_type=pt, distance=15.0, lane_quality=0.7,
                is_under_pressure=False, has_needle_threader=False,
                has_bail_out=False, rng=SeededRNG(42),
            )
            assert isinstance(result.completed, bool)
