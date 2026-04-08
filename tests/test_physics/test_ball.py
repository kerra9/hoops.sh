"""Tests for Ball physics."""

from __future__ import annotations

import pytest

from hoops_sim.physics.ball import Ball, BallState
from hoops_sim.physics.vec import Vec3


class TestBall:
    def test_default_state(self):
        ball = Ball()
        assert ball.state == BallState.DEAD
        assert ball.position.magnitude() == 0.0

    def test_set_held(self):
        ball = Ball()
        pos = Vec3(10.0, 25.0, 7.0)
        ball.set_held(pos)
        assert ball.state == BallState.HELD
        assert ball.position.x == 10.0
        assert ball.velocity.magnitude() == 0.0

    def test_launch_shot(self):
        ball = Ball()
        ball.set_held(Vec3(20.0, 25.0, 8.0))
        velocity = Vec3(5.0, 0.0, 15.0)
        spin = Vec3(180.0, 0.0, 0.0)
        ball.launch_shot(velocity, spin)
        assert ball.state == BallState.IN_FLIGHT_SHOT
        assert ball.velocity.z == pytest.approx(15.0)
        assert ball.spin.x == pytest.approx(180.0)

    def test_launch_pass(self):
        ball = Ball()
        ball.set_held(Vec3(10.0, 10.0, 6.0))
        ball.launch_pass(Vec3(20.0, 5.0, 1.0))
        assert ball.state == BallState.IN_FLIGHT_PASS

    def test_flight_gravity(self):
        ball = Ball()
        ball.position = Vec3(0.0, 0.0, 20.0)
        ball.velocity = Vec3(10.0, 0.0, 0.0)
        ball.state = BallState.IN_FLIGHT_SHOT

        # After one tick, z-velocity should decrease due to gravity
        ball.update_flight(0.1)
        assert ball.velocity.z < 0.0  # Gravity pulls down
        assert ball.position.x > 0.0  # Moved forward

    def test_flight_not_updated_when_held(self):
        ball = Ball()
        ball.position = Vec3(5.0, 5.0, 7.0)
        ball.velocity = Vec3(10.0, 0.0, 10.0)
        ball.state = BallState.HELD

        ball.update_flight(0.1)
        # Position should not change
        assert ball.position.x == pytest.approx(5.0)

    def test_bounce_off_floor(self):
        ball = Ball()
        ball.position = Vec3(10.0, 10.0, 0.1)  # Near floor
        ball.velocity = Vec3(5.0, 0.0, -10.0)  # Moving down
        ball.state = BallState.LOOSE

        ball.bounce_off_floor()
        assert ball.velocity.z > 0.0  # Bounced up
        assert ball.velocity.z < 10.0  # Lost energy (COR < 1)

    def test_make_loose(self):
        ball = Ball()
        ball.set_held(Vec3(0.0, 0.0, 6.0))
        ball.make_loose()
        assert ball.state == BallState.LOOSE

    def test_make_dead(self):
        ball = Ball()
        ball.velocity = Vec3(10.0, 5.0, 3.0)
        ball.state = BallState.IN_FLIGHT_SHOT
        ball.make_dead()
        assert ball.state == BallState.DEAD
        assert ball.velocity.magnitude() == 0.0

    def test_is_airborne(self):
        ball = Ball()
        ball.position = Vec3(0.0, 0.0, 5.0)
        assert ball.is_airborne()

        ball.position = Vec3(0.0, 0.0, 0.1)
        assert not ball.is_airborne()
