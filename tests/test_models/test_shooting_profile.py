"""Tests for shooting profile / hot zone system."""

from __future__ import annotations

import pytest

from hoops_sim.court.zones import Zone
from hoops_sim.models.shooting_profile import ShootingProfile, ZoneRating


class TestShootingProfile:
    def test_default_neutral(self):
        profile = ShootingProfile()
        assert profile.get_modifier(Zone.RESTRICTED) == 0
        assert profile.get_rating(Zone.RESTRICTED) == ZoneRating.NEUTRAL

    def test_all_zones_initialized(self):
        profile = ShootingProfile()
        for zone in Zone:
            assert profile.get_modifier(zone) == 0

    def test_set_modifier(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_TOP_KEY, 10)
        assert profile.get_modifier(Zone.THREE_TOP_KEY) == 10

    def test_modifier_clamped(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_TOP_KEY, 20)
        assert profile.get_modifier(Zone.THREE_TOP_KEY) == 15

        profile.set_modifier(Zone.THREE_TOP_KEY, -20)
        assert profile.get_modifier(Zone.THREE_TOP_KEY) == -15

    def test_hot_zone(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_LEFT_CORNER, 8)
        assert profile.get_rating(Zone.THREE_LEFT_CORNER) == ZoneRating.HOT

    def test_cold_zone(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.MID_LEFT_WING, -7)
        assert profile.get_rating(Zone.MID_LEFT_WING) == ZoneRating.COLD

    def test_effective_rating(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_TOP_KEY, 5)
        assert profile.get_effective_rating(Zone.THREE_TOP_KEY, 80) == 85

    def test_effective_rating_clamped(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_TOP_KEY, 15)
        assert profile.get_effective_rating(Zone.THREE_TOP_KEY, 95) == 99

    def test_hot_zones_list(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.THREE_LEFT_CORNER, 8)
        profile.set_modifier(Zone.THREE_RIGHT_CORNER, 10)
        hot = profile.hot_zones()
        assert Zone.THREE_LEFT_CORNER in hot
        assert Zone.THREE_RIGHT_CORNER in hot
        assert len(hot) == 2

    def test_cold_zones_list(self):
        profile = ShootingProfile()
        profile.set_modifier(Zone.MID_LEFT_WING, -8)
        cold = profile.cold_zones()
        assert Zone.MID_LEFT_WING in cold
        assert len(cold) == 1

    def test_zone_count_by_rating(self):
        profile = ShootingProfile()
        counts = profile.zone_count_by_rating()
        assert counts[ZoneRating.NEUTRAL] == 17
        assert counts[ZoneRating.HOT] == 0
        assert counts[ZoneRating.COLD] == 0
