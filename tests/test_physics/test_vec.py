"""Tests for Vec2 and Vec3 math utilities."""

from __future__ import annotations

import math

import pytest

from hoops_sim.physics.vec import Vec2, Vec3, distance_2d


class TestVec2:
    def test_creation_defaults(self):
        v = Vec2()
        assert v.x == 0.0
        assert v.y == 0.0

    def test_creation_with_values(self):
        v = Vec2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_addition(self):
        a = Vec2(1.0, 2.0)
        b = Vec2(3.0, 4.0)
        result = a + b
        assert result.x == pytest.approx(4.0)
        assert result.y == pytest.approx(6.0)

    def test_subtraction(self):
        a = Vec2(5.0, 7.0)
        b = Vec2(2.0, 3.0)
        result = a - b
        assert result.x == pytest.approx(3.0)
        assert result.y == pytest.approx(4.0)

    def test_scalar_multiply(self):
        v = Vec2(3.0, 4.0)
        result = v * 2.0
        assert result.x == pytest.approx(6.0)
        assert result.y == pytest.approx(8.0)

    def test_rmul(self):
        v = Vec2(3.0, 4.0)
        result = 2.0 * v
        assert result.x == pytest.approx(6.0)
        assert result.y == pytest.approx(8.0)

    def test_division(self):
        v = Vec2(6.0, 8.0)
        result = v / 2.0
        assert result.x == pytest.approx(3.0)
        assert result.y == pytest.approx(4.0)

    def test_negation(self):
        v = Vec2(3.0, -4.0)
        result = -v
        assert result.x == pytest.approx(-3.0)
        assert result.y == pytest.approx(4.0)

    def test_magnitude(self):
        v = Vec2(3.0, 4.0)
        assert v.magnitude() == pytest.approx(5.0)

    def test_magnitude_squared(self):
        v = Vec2(3.0, 4.0)
        assert v.magnitude_squared() == pytest.approx(25.0)

    def test_normalized(self):
        v = Vec2(3.0, 4.0)
        n = v.normalized()
        assert n.magnitude() == pytest.approx(1.0)
        assert n.x == pytest.approx(0.6)
        assert n.y == pytest.approx(0.8)

    def test_normalized_zero_vector(self):
        v = Vec2(0.0, 0.0)
        n = v.normalized()
        assert n.x == 0.0
        assert n.y == 0.0

    def test_dot_product(self):
        a = Vec2(1.0, 0.0)
        b = Vec2(0.0, 1.0)
        assert a.dot(b) == pytest.approx(0.0)

        c = Vec2(2.0, 3.0)
        d = Vec2(4.0, 5.0)
        assert c.dot(d) == pytest.approx(23.0)

    def test_cross_product(self):
        a = Vec2(1.0, 0.0)
        b = Vec2(0.0, 1.0)
        assert a.cross(b) == pytest.approx(1.0)

    def test_angle(self):
        assert Vec2(1.0, 0.0).angle() == pytest.approx(0.0)
        assert Vec2(0.0, 1.0).angle() == pytest.approx(90.0)
        assert Vec2(-1.0, 0.0).angle() == pytest.approx(180.0)

    def test_distance_to(self):
        a = Vec2(0.0, 0.0)
        b = Vec2(3.0, 4.0)
        assert a.distance_to(b) == pytest.approx(5.0)

    def test_rotate(self):
        v = Vec2(1.0, 0.0)
        rotated = v.rotate(90.0)
        assert rotated.x == pytest.approx(0.0, abs=1e-10)
        assert rotated.y == pytest.approx(1.0)

    def test_lerp(self):
        a = Vec2(0.0, 0.0)
        b = Vec2(10.0, 10.0)
        mid = a.lerp(b, 0.5)
        assert mid.x == pytest.approx(5.0)
        assert mid.y == pytest.approx(5.0)

    def test_lerp_clamped(self):
        a = Vec2(0.0, 0.0)
        b = Vec2(10.0, 10.0)
        beyond = a.lerp(b, 1.5)
        assert beyond.x == pytest.approx(10.0)
        assert beyond.y == pytest.approx(10.0)

    def test_from_angle(self):
        v = Vec2.from_angle(0.0, 5.0)
        assert v.x == pytest.approx(5.0)
        assert v.y == pytest.approx(0.0, abs=1e-10)

        v2 = Vec2.from_angle(90.0, 3.0)
        assert v2.x == pytest.approx(0.0, abs=1e-10)
        assert v2.y == pytest.approx(3.0)

    def test_copy(self):
        v = Vec2(3.0, 4.0)
        c = v.copy()
        assert c.x == v.x
        assert c.y == v.y
        c.x = 99.0
        assert v.x == 3.0  # Original unchanged

    def test_iadd(self):
        v = Vec2(1.0, 2.0)
        v += Vec2(3.0, 4.0)
        assert v.x == pytest.approx(4.0)
        assert v.y == pytest.approx(6.0)

    def test_zero(self):
        v = Vec2.zero()
        assert v.x == 0.0
        assert v.y == 0.0


class TestVec3:
    def test_creation_defaults(self):
        v = Vec3()
        assert v.x == 0.0
        assert v.y == 0.0
        assert v.z == 0.0

    def test_addition(self):
        a = Vec3(1.0, 2.0, 3.0)
        b = Vec3(4.0, 5.0, 6.0)
        result = a + b
        assert result.x == pytest.approx(5.0)
        assert result.y == pytest.approx(7.0)
        assert result.z == pytest.approx(9.0)

    def test_subtraction(self):
        a = Vec3(5.0, 7.0, 9.0)
        b = Vec3(1.0, 2.0, 3.0)
        result = a - b
        assert result.x == pytest.approx(4.0)
        assert result.y == pytest.approx(5.0)
        assert result.z == pytest.approx(6.0)

    def test_magnitude(self):
        v = Vec3(1.0, 2.0, 2.0)
        assert v.magnitude() == pytest.approx(3.0)

    def test_normalized(self):
        v = Vec3(0.0, 0.0, 5.0)
        n = v.normalized()
        assert n.z == pytest.approx(1.0)
        assert n.magnitude() == pytest.approx(1.0)

    def test_dot_product(self):
        a = Vec3(1.0, 0.0, 0.0)
        b = Vec3(0.0, 1.0, 0.0)
        assert a.dot(b) == pytest.approx(0.0)

    def test_cross_product(self):
        a = Vec3(1.0, 0.0, 0.0)
        b = Vec3(0.0, 1.0, 0.0)
        result = a.cross(b)
        assert result.z == pytest.approx(1.0)

    def test_xy_projection(self):
        v = Vec3(3.0, 4.0, 10.0)
        xy = v.xy()
        assert xy.x == 3.0
        assert xy.y == 4.0

    def test_from_angle_and_speed(self):
        # Straight up
        v = Vec3.from_angle_and_speed(90.0, 10.0, 0.0)
        assert v.z == pytest.approx(10.0)
        assert abs(v.x) < 0.01
        assert abs(v.y) < 0.01

        # Flat, heading right
        v2 = Vec3.from_angle_and_speed(0.0, 10.0, 0.0)
        assert v2.x == pytest.approx(10.0)
        assert abs(v2.z) < 0.01

    def test_distance_to(self):
        a = Vec3(0.0, 0.0, 0.0)
        b = Vec3(1.0, 2.0, 2.0)
        assert a.distance_to(b) == pytest.approx(3.0)

    def test_lerp(self):
        a = Vec3(0.0, 0.0, 0.0)
        b = Vec3(10.0, 10.0, 10.0)
        mid = a.lerp(b, 0.5)
        assert mid.x == pytest.approx(5.0)
        assert mid.z == pytest.approx(5.0)

    def test_copy(self):
        v = Vec3(1.0, 2.0, 3.0)
        c = v.copy()
        c.x = 99.0
        assert v.x == 1.0

    def test_zero(self):
        v = Vec3.zero()
        assert v.magnitude() == 0.0


class TestDistance2D:
    def test_vec2_distance(self):
        a = Vec2(0.0, 0.0)
        b = Vec2(3.0, 4.0)
        assert distance_2d(a, b) == pytest.approx(5.0)

    def test_vec3_distance_ignores_z(self):
        a = Vec3(0.0, 0.0, 0.0)
        b = Vec3(3.0, 4.0, 100.0)
        assert distance_2d(a, b) == pytest.approx(5.0)
