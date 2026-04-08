"""Tests for contact detection and resolution."""

from __future__ import annotations

import pytest

from hoops_sim.physics.contact import (
    ContactSeverity,
    ContactType,
    classify_severity,
    detect_contact,
)
from hoops_sim.physics.vec import Vec2


class TestClassifySeverity:
    def test_none(self):
        assert classify_severity(0.1) == ContactSeverity.NONE

    def test_incidental(self):
        assert classify_severity(0.25) == ContactSeverity.INCIDENTAL

    def test_light(self):
        assert classify_severity(0.45) == ContactSeverity.LIGHT

    def test_moderate(self):
        assert classify_severity(0.65) == ContactSeverity.MODERATE

    def test_hard(self):
        assert classify_severity(0.85) == ContactSeverity.HARD

    def test_flagrant(self):
        assert classify_severity(0.95) == ContactSeverity.FLAGRANT


class TestDetectContact:
    def test_no_contact_far_apart(self):
        result = detect_contact(
            off_pos=Vec2(0.0, 0.0),
            off_vel=Vec2(5.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(20.0, 0.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=210.0,
        )
        assert result is None

    def test_contact_when_close(self):
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(10.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=210.0,
        )
        assert result is not None
        assert result.severity != ContactSeverity.NONE

    def test_contact_point_between_players(self):
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(5.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(12.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=210.0,
        )
        assert result is not None
        cp = result.contact_point
        assert 10.0 <= cp.x <= 12.0
        assert cp.y == pytest.approx(10.0)

    def test_relative_velocity(self):
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(15.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.5, 10.0),
            def_vel=Vec2(-5.0, 0.0),
            def_weight=210.0,
        )
        assert result is not None
        assert result.relative_velocity == pytest.approx(20.0)

    def test_defensive_set(self):
        """Stationary defender should be marked as set."""
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(10.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=210.0,
        )
        assert result is not None
        assert result.defensive_set is True

    def test_defender_not_set_when_moving(self):
        """Moving defender should not be set."""
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(10.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(-5.0, 0.0),
            def_weight=210.0,
        )
        assert result is not None
        assert result.defensive_set is False

    def test_force_calculation(self):
        result = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(15.0, 0.0),
            off_weight=220.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=200.0,
        )
        assert result is not None
        assert result.force > 0
        assert result.offensive_momentum > 0

    def test_higher_speed_higher_severity(self):
        slow = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(3.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=200.0,
        )
        fast = detect_contact(
            off_pos=Vec2(10.0, 10.0),
            off_vel=Vec2(18.0, 0.0),
            off_weight=200.0,
            def_pos=Vec2(11.0, 10.0),
            def_vel=Vec2(0.0, 0.0),
            def_weight=200.0,
        )
        assert slow is not None and fast is not None
        assert fast.severity_value >= slow.severity_value
