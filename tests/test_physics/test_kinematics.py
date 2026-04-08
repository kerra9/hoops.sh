"""Tests for player kinematics."""

from __future__ import annotations

import pytest

from hoops_sim.physics.kinematics import MovementType, PlayerKinematics
from hoops_sim.physics.vec import Vec2


class TestPlayerKinematics:
    def test_from_attributes(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(47.0, 25.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        assert pk.max_sprint_speed > 20.0
        assert pk.acceleration > 10.0
        assert pk.lateral_speed > 0

    def test_standing_still_no_energy(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        energy = pk.update(0.1, Vec2(0.0, 0.0), MovementType.STAND)
        assert energy >= 0

    def test_movement_changes_position(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        target = Vec2(50.0, 0.0)

        # Simulate several ticks of sprinting
        for _ in range(20):
            pk.update(0.1, target, MovementType.SPRINT)

        assert pk.position.x > 0.0  # Player moved toward target
        assert pk.velocity.magnitude() > 0.0  # Player has velocity

    def test_sprint_faster_than_jog(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=90,
            lateral_quickness_attr=70,
        )
        sprint_speed = pk.get_speed_for_type(MovementType.SPRINT)
        jog_speed = pk.get_speed_for_type(MovementType.JOG)
        assert sprint_speed > jog_speed

    def test_backpedal_slower_than_sprint(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        sprint = pk.get_speed_for_type(MovementType.SPRINT)
        backpedal = pk.get_speed_for_type(MovementType.BACKPEDAL)
        assert backpedal < sprint

    def test_energy_cost_increases_with_speed(self):
        pk1 = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=90,
            lateral_quickness_attr=70,
        )
        pk2 = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=90,
            lateral_quickness_attr=70,
        )
        target = Vec2(100.0, 0.0)

        # Sprint for a few ticks to build speed
        sprint_energy = 0.0
        for _ in range(10):
            sprint_energy += pk1.update(0.1, target, MovementType.SPRINT)

        walk_energy = 0.0
        for _ in range(10):
            walk_energy += pk2.update(0.1, target, MovementType.WALK)

        assert sprint_energy > walk_energy

    def test_deceleration_when_standing(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        # First build up some speed
        for _ in range(10):
            pk.update(0.1, Vec2(100.0, 0.0), MovementType.SPRINT)

        speed_before = pk.current_speed()
        assert speed_before > 0

        # Now stand still - should decelerate
        for _ in range(20):
            pk.update(0.1, pk.position, MovementType.STAND)

        assert pk.current_speed() < speed_before

    def test_is_moving(self):
        pk = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=80,
            acceleration_attr=75,
            lateral_quickness_attr=70,
        )
        assert not pk.is_moving()

        pk.update(0.1, Vec2(50.0, 0.0), MovementType.SPRINT)
        assert pk.is_moving()

    def test_higher_speed_attr_faster(self):
        slow = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=30,
            acceleration_attr=50,
            lateral_quickness_attr=50,
        )
        fast = PlayerKinematics.from_attributes(
            position=Vec2(0.0, 0.0),
            speed_attr=95,
            acceleration_attr=50,
            lateral_quickness_attr=50,
        )
        assert fast.max_sprint_speed > slow.max_sprint_speed
