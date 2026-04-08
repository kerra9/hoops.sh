"""Tests for court surface model."""

from __future__ import annotations

import pytest

from hoops_sim.physics.court_surface import (
    CourtSurface,
    DENVER_SURFACE,
    DEFAULT_SURFACE,
    MIAMI_SURFACE,
    ShoeGrip,
    SurfaceCondition,
)


class TestCourtSurface:
    def test_default_traction(self):
        surface = CourtSurface()
        traction = surface.get_traction()
        assert 0.85 <= traction <= 1.0

    def test_worn_surface_lower_traction(self):
        good = CourtSurface(condition=SurfaceCondition.GOOD)
        worn = CourtSurface(condition=SurfaceCondition.WORN)
        assert worn.get_traction() < good.get_traction()

    def test_humid_surface_lower_traction(self):
        dry = CourtSurface(humidity_pct=30)
        humid = CourtSurface(humidity_pct=75)
        assert humid.get_traction() < dry.get_traction()

    def test_shoe_grip_affects_traction(self):
        surface = CourtSurface()
        good_shoes = ShoeGrip(grip=0.98)
        bad_shoes = ShoeGrip(grip=0.80)
        assert surface.get_traction(good_shoes) > surface.get_traction(bad_shoes)

    def test_traction_clamped(self):
        surface = CourtSurface(grip_coefficient=1.2)  # Unrealistically high
        assert surface.get_traction() <= 1.0

        surface2 = CourtSurface(
            grip_coefficient=0.3,
            condition=SurfaceCondition.WORN,
            humidity_pct=90,
        )
        assert surface2.get_traction() >= 0.5


class TestAltitudeEffects:
    def test_sea_level_no_stamina_effect(self):
        surface = CourtSurface(altitude_ft=0)
        assert surface.get_stamina_drain_modifier() == pytest.approx(1.0)

    def test_denver_higher_stamina_drain(self):
        assert DENVER_SURFACE.get_stamina_drain_modifier() > 1.0

    def test_altitude_ball_bounce(self):
        surface = CourtSurface(altitude_ft=5280)
        assert surface.get_ball_bounce_modifier() > 1.0

    def test_sea_level_no_bounce_effect(self):
        surface = CourtSurface(altitude_ft=0)
        assert surface.get_ball_bounce_modifier() == pytest.approx(1.0)


class TestSlipProbability:
    def test_good_traction_low_slip(self):
        surface = CourtSurface(condition=SurfaceCondition.EXCELLENT)
        assert surface.get_slip_probability() < 0.005

    def test_worn_surface_higher_slip(self):
        good = CourtSurface(condition=SurfaceCondition.EXCELLENT)
        worn = CourtSurface(
            condition=SurfaceCondition.WORN,
            humidity_pct=80,
        )
        assert worn.get_slip_probability() > good.get_slip_probability()


class TestPreConfigured:
    def test_denver_has_altitude(self):
        assert DENVER_SURFACE.altitude_ft == 5280

    def test_miami_has_humidity(self):
        assert MIAMI_SURFACE.humidity_pct > 50

    def test_default_surface_reasonable(self):
        assert DEFAULT_SURFACE.condition == SurfaceCondition.GOOD
        assert DEFAULT_SURFACE.altitude_ft == 0
