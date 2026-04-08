"""Tests for free throw model."""

from __future__ import annotations

import pytest

from hoops_sim.shot.free_throw import simulate_free_throw
from hoops_sim.utils.rng import SeededRNG


def _ft_make_rate(n: int = 500, **kwargs) -> float:
    """Run n free throws and return make rate."""
    made = sum(
        1 for seed in range(n)
        if simulate_free_throw(rng=SeededRNG(seed), **kwargs)
    )
    return made / n


class TestFreeThrow:
    def test_good_ft_shooter(self):
        rate = _ft_make_rate(
            ft_rating=85, energy_pct=1.0, composure=80, clutch=70,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        assert 0.70 < rate < 0.95

    def test_bad_ft_shooter(self):
        rate = _ft_make_rate(
            ft_rating=45, energy_pct=1.0, composure=60, clutch=50,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        assert rate < 0.60

    def test_fatigue_hurts(self):
        fresh = _ft_make_rate(
            ft_rating=80, energy_pct=1.0, composure=70, clutch=70,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        tired = _ft_make_rate(
            ft_rating=80, energy_pct=0.2, composure=70, clutch=70,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        assert fresh >= tired

    def test_icing_hurts(self):
        normal = _ft_make_rate(
            ft_rating=80, energy_pct=1.0, composure=50, clutch=50,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        iced = _ft_make_rate(
            ft_rating=80, energy_pct=1.0, composure=50, clutch=50,
            is_clutch_time=False, was_timeout_before_ft=True,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        assert normal >= iced

    def test_hostile_crowd_hurts_away(self):
        home = _ft_make_rate(
            ft_rating=75, energy_pct=1.0, composure=50, clutch=50,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=95, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        away = _ft_make_rate(
            ft_rating=75, energy_pct=1.0, composure=50, clutch=50,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=False, crowd_energy=95, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
        )
        assert home >= away

    def test_deterministic(self):
        r1 = simulate_free_throw(
            ft_rating=80, energy_pct=1.0, composure=70, clutch=70,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
            rng=SeededRNG(42),
        )
        r2 = simulate_free_throw(
            ft_rating=80, energy_pct=1.0, composure=70, clutch=70,
            is_clutch_time=False, was_timeout_before_ft=False,
            is_home=True, crowd_energy=50, ice_in_veins_tier=0,
            ft_number=1, previous_ft_made=True, lane_violation=False,
            rng=SeededRNG(42),
        )
        assert r1 == r2
