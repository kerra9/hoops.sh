"""Tests for court model."""

from __future__ import annotations

import pytest

from hoops_sim.court.model import (
    distance_to_basket,
    get_basket_position,
    is_in_bounds,
    is_in_frontcourt,
    is_in_paint,
    is_in_restricted_area,
    is_three_point,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    BASKET_X,
    BASKET_Y,
    COURT_LENGTH,
    COURT_WIDTH,
    HALF_COURT_LENGTH,
)


class TestIsInBounds:
    def test_center_court(self):
        assert is_in_bounds(Vec2(47.0, 25.0))

    def test_corner(self):
        assert is_in_bounds(Vec2(0.0, 0.0))

    def test_out_of_bounds(self):
        assert not is_in_bounds(Vec2(-1.0, 25.0))
        assert not is_in_bounds(Vec2(95.0, 25.0))
        assert not is_in_bounds(Vec2(47.0, -1.0))
        assert not is_in_bounds(Vec2(47.0, 51.0))


class TestFrontcourt:
    def test_attacking_right(self):
        assert is_in_frontcourt(Vec2(50.0, 25.0), attacking_right=True)
        assert not is_in_frontcourt(Vec2(40.0, 25.0), attacking_right=True)

    def test_attacking_left(self):
        assert is_in_frontcourt(Vec2(40.0, 25.0), attacking_right=False)
        assert not is_in_frontcourt(Vec2(50.0, 25.0), attacking_right=False)


class TestBasketPosition:
    def test_right_basket(self):
        basket = get_basket_position(attacking_right=True)
        assert basket.x == pytest.approx(COURT_LENGTH - BASKET_X)
        assert basket.y == pytest.approx(BASKET_Y)

    def test_left_basket(self):
        basket = get_basket_position(attacking_right=False)
        assert basket.x == pytest.approx(BASKET_X)
        assert basket.y == pytest.approx(BASKET_Y)


class TestDistanceToBasket:
    def test_at_basket(self):
        basket = get_basket_position(True)
        assert distance_to_basket(basket, True) == pytest.approx(0.0)

    def test_half_court(self):
        dist = distance_to_basket(Vec2(HALF_COURT_LENGTH, BASKET_Y), True)
        expected = COURT_LENGTH - BASKET_X - HALF_COURT_LENGTH
        assert dist == pytest.approx(expected)


class TestPaint:
    def test_under_basket_is_paint(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 2.0, basket.y)
        assert is_in_paint(pos, True)

    def test_outside_paint(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 25.0, basket.y)
        assert not is_in_paint(pos, True)

    def test_wing_not_paint(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 10.0, basket.y + 15.0)
        assert not is_in_paint(pos, True)


class TestRestrictedArea:
    def test_under_basket(self):
        basket = get_basket_position(True)
        assert is_in_restricted_area(basket, True)

    def test_just_outside(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 5.0, basket.y)
        assert not is_in_restricted_area(pos, True)


class TestThreePoint:
    def test_at_rim_not_three(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 5.0, basket.y)
        assert not is_three_point(pos, True)

    def test_beyond_arc(self):
        basket = get_basket_position(True)
        pos = Vec2(basket.x - 24.0, basket.y)
        assert is_three_point(pos, True)

    def test_corner_three(self):
        basket = get_basket_position(True)
        # Corner position: near sideline, 22+ feet from basket
        pos = Vec2(basket.x - 1.0, 1.0)
        dist = pos.distance_to(basket)
        if dist >= 22.0:
            assert is_three_point(pos, True)
