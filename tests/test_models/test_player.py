"""Tests for the complete Player model."""

from __future__ import annotations

import pytest

from hoops_sim.models.attributes import PlayerAttributes, ShootingAttributes, AthleticAttributes
from hoops_sim.models.badges import BadgeTier, PlayerBadges
from hoops_sim.models.body import PlayerBody
from hoops_sim.models.player import Player, Position


class TestPlayer:
    def test_defaults(self):
        p = Player()
        assert p.position == Position.SF
        assert p.age == 25
        assert p.overall >= 0

    def test_full_name(self):
        p = Player(first_name="LeBron", last_name="James")
        assert p.full_name == "LeBron James"

    def test_overall_calculation(self):
        p = Player()
        p.attributes = PlayerAttributes(
            shooting=ShootingAttributes(
                close_shot=80, mid_range=85, three_point=82,
                free_throw=78, shot_iq=80, shot_consistency=82, shot_speed=80,
            ),
        )
        assert p.overall > 50  # Shooting is above average

    def test_max_energy(self):
        p = Player()
        p.attributes.athleticism.stamina = 90
        max_e = p.max_energy()
        assert max_e > 100  # Stamina bonus

    def test_energy_pct(self):
        p = Player()
        p.current_energy = 50.0
        pct = p.energy_pct()
        assert 0.0 < pct < 1.0

    def test_is_fatigued(self):
        p = Player()
        p.current_energy = 30.0  # Low energy
        assert p.is_fatigued()

        p.current_energy = 100.0
        assert not p.is_fatigued()

    def test_is_exhausted(self):
        p = Player()
        p.current_energy = 10.0
        assert p.is_exhausted()

    def test_vertical_leap(self):
        p = Player()
        p.attributes.athleticism.vertical_leap = 99
        leap = p.vertical_leap_inches()
        assert leap > 40

        p.attributes.athleticism.vertical_leap = 1
        leap = p.vertical_leap_inches()
        assert leap < 26

    def test_can_play_position(self):
        p = Player(position=Position.SF, secondary_position=Position.PF)
        assert p.can_play_position(Position.SF)
        assert p.can_play_position(Position.PF)
        assert not p.can_play_position(Position.PG)

    def test_is_rookie(self):
        p = Player(years_pro=0)
        assert p.is_rookie()
        p2 = Player(years_pro=5)
        assert not p2.is_rookie()

    def test_is_veteran(self):
        p = Player(years_pro=12)
        assert p.is_veteran()
        p2 = Player(years_pro=5)
        assert not p2.is_veteran()

    def test_repr(self):
        p = Player(first_name="Steph", last_name="Curry", position=Position.PG, age=35)
        s = repr(p)
        assert "Steph Curry" in s
        assert "PG" in s
        assert "35" in s


class TestPosition:
    def test_all_positions(self):
        assert len(Position) == 5
        assert Position.PG.value == "PG"
        assert Position.C.value == "C"
