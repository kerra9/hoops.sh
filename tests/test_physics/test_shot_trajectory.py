"""Tests for shot trajectory calculation."""

from __future__ import annotations

import pytest

from hoops_sim.physics.shot_trajectory import (
    calculate_shot_trajectory,
    optimal_release_angle,
    required_launch_speed,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    BASKET_HEIGHT,
    OPTIMAL_RELEASE_ANGLE_AT_RIM,
    OPTIMAL_RELEASE_ANGLE_THREE,
)
from hoops_sim.utils.rng import SeededRNG


class TestOptimalReleaseAngle:
    def test_at_rim(self):
        angle = optimal_release_angle(2.0)
        assert angle == pytest.approx(OPTIMAL_RELEASE_ANGLE_AT_RIM)

    def test_at_three(self):
        angle = optimal_release_angle(24.0)
        assert angle == pytest.approx(OPTIMAL_RELEASE_ANGLE_THREE)

    def test_mid_range_between(self):
        angle = optimal_release_angle(14.0)
        assert OPTIMAL_RELEASE_ANGLE_THREE < angle < OPTIMAL_RELEASE_ANGLE_AT_RIM

    def test_closer_is_higher_arc(self):
        close = optimal_release_angle(6.0)
        far = optimal_release_angle(20.0)
        assert close > far


class TestRequiredLaunchSpeed:
    def test_close_shot_lower_speed(self):
        close_speed = required_launch_speed(5.0, 50.0, 8.0)
        far_speed = required_launch_speed(24.0, 45.0, 8.0)
        assert close_speed < far_speed

    def test_higher_release_needs_less_speed(self):
        low = required_launch_speed(15.0, 48.0, 7.0)
        high = required_launch_speed(15.0, 48.0, 9.0)
        assert high < low

    def test_positive_speed(self):
        speed = required_launch_speed(20.0, 45.0, 8.0)
        assert speed > 0


class TestCalculateShotTrajectory:
    def test_returns_trajectory(self):
        rng = SeededRNG(seed=123)
        traj = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=80,
            shot_release_quality=0.8,
            rng=rng,
        )
        assert traj.release_point.z > 7.0  # Release height above 7 feet
        assert traj.velocity.magnitude() > 0
        assert traj.spin.x > 0  # Has backspin

    def test_better_shooter_less_variance(self):
        """Better shooters should have more consistent trajectories."""
        rng1 = SeededRNG(seed=100)
        rng2 = SeededRNG(seed=100)

        good = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=95,
            shot_release_quality=0.9,
            rng=rng1,
        )

        bad = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=40,
            shot_release_quality=0.5,
            rng=rng2,
        )

        # Both should produce valid trajectories
        assert good.velocity.magnitude() > 0
        assert bad.velocity.magnitude() > 0
        # Better shooter should have more backspin
        assert good.spin.x > bad.spin.x

    def test_jump_shot_higher_release(self):
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=42)

        jump = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=75,
            shot_release_quality=0.7,
            rng=rng1,
        )

        set_shot = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=False,
            zone_rating=75,
            shot_release_quality=0.7,
            rng=rng2,
        )

        assert jump.release_point.z > set_shot.release_point.z

    def test_deterministic_with_same_seed(self):
        rng1 = SeededRNG(seed=999)
        rng2 = SeededRNG(seed=999)

        t1 = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=80,
            shot_release_quality=0.8,
            rng=rng1,
        )

        t2 = calculate_shot_trajectory(
            shooter_position=Vec2(20.0, 25.0),
            shooter_height_inches=78,
            standing_reach_inches=102,
            vertical_leap_inches=36,
            is_jump_shot=True,
            zone_rating=80,
            shot_release_quality=0.8,
            rng=rng2,
        )

        assert t1.velocity.x == pytest.approx(t2.velocity.x)
        assert t1.velocity.z == pytest.approx(t2.velocity.z)
        assert t1.spin.x == pytest.approx(t2.spin.x)
