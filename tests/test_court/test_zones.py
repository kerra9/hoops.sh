"""Tests for court zones."""

from __future__ import annotations

import pytest

from hoops_sim.court.zones import Zone, get_zone, get_zone_info
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import BASKET_X, BASKET_Y, COURT_LENGTH


class TestGetZone:
    """Test zone classification for positions attacking the right basket."""

    def test_restricted_area(self):
        """Position right under the basket."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 1.0, basket.y)
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.RESTRICTED

    def test_close_middle(self):
        """Position ~7 feet from basket, straight on."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 7.0, basket.y)
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.CLOSE_MIDDLE

    def test_mid_free_throw(self):
        """Position at the free throw line."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 15.0, basket.y)
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.MID_FREE_THROW

    def test_three_top_key(self):
        """Position at the top of the arc, 24+ feet."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 24.0, basket.y)
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.THREE_TOP_KEY

    def test_corner_three_right(self):
        """Position in the right corner (bottom sideline)."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 1.0, 1.5)  # Near bottom sideline
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.THREE_RIGHT_CORNER

    def test_corner_three_left(self):
        """Position in the left corner (top sideline)."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 1.0, 48.5)  # Near top sideline
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.THREE_LEFT_CORNER

    def test_deep_three(self):
        """Position beyond 28 feet."""
        basket = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)
        pos = Vec2(basket.x - 30.0, basket.y)
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.DEEP_THREE

    def test_backcourt_is_deep(self):
        """Position in the backcourt should be deep three."""
        pos = Vec2(20.0, 25.0)  # Backcourt when attacking right
        zone = get_zone(pos, attacking_right=True)
        assert zone == Zone.DEEP_THREE


class TestGetZoneInfo:
    def test_restricted_info(self):
        info = get_zone_info(Zone.RESTRICTED)
        assert info.is_paint is True
        assert info.is_three is False
        assert info.name == "Restricted Area"

    def test_three_point_info(self):
        info = get_zone_info(Zone.THREE_TOP_KEY)
        assert info.is_three is True
        assert info.is_paint is False

    def test_corner_three_info(self):
        info = get_zone_info(Zone.THREE_LEFT_CORNER)
        assert info.is_three is True
        assert info.avg_distance == pytest.approx(22.0)

    def test_all_zones_have_info(self):
        """Every zone should have metadata."""
        for zone in Zone:
            info = get_zone_info(zone)
            assert info.name
            assert info.short_name
            assert info.avg_distance > 0
