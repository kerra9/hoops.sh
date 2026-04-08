"""Tests for badge system."""

from __future__ import annotations

import pytest

from hoops_sim.models.badges import (
    BADGE_DEFINITIONS,
    BadgeCategory,
    BadgeTier,
    PlayerBadges,
)


class TestBadgeDefinitions:
    def test_has_30_plus_badges(self):
        assert len(BADGE_DEFINITIONS) >= 30

    def test_all_categories_represented(self):
        categories = {d.category for d in BADGE_DEFINITIONS.values()}
        assert BadgeCategory.SHOOTING in categories
        assert BadgeCategory.FINISHING in categories
        assert BadgeCategory.PLAYMAKING in categories
        assert BadgeCategory.DEFENSE in categories
        assert BadgeCategory.REBOUNDING in categories
        assert BadgeCategory.MENTAL in categories


class TestBadgeTier:
    def test_ordering(self):
        assert BadgeTier.BRONZE < BadgeTier.SILVER
        assert BadgeTier.SILVER < BadgeTier.GOLD
        assert BadgeTier.GOLD < BadgeTier.HALL_OF_FAME

    def test_values(self):
        assert int(BadgeTier.BRONZE) == 1
        assert int(BadgeTier.HALL_OF_FAME) == 4


class TestPlayerBadges:
    def test_empty(self):
        badges = PlayerBadges()
        assert badges.count() == 0
        assert not badges.has_badge("deadeye")

    def test_add_badge(self):
        badges = PlayerBadges()
        badges.add_badge("deadeye", BadgeTier.GOLD)
        assert badges.has_badge("deadeye")
        assert badges.get_tier("deadeye") == BadgeTier.GOLD

    def test_add_invalid_badge(self):
        badges = PlayerBadges()
        with pytest.raises(ValueError):
            badges.add_badge("nonexistent_badge", BadgeTier.BRONZE)

    def test_tier_value(self):
        badges = PlayerBadges()
        assert badges.tier_value("deadeye") == 0
        badges.add_badge("deadeye", BadgeTier.SILVER)
        assert badges.tier_value("deadeye") == 2

    def test_tier_multiplier(self):
        badges = PlayerBadges()
        assert badges.tier_multiplier("deadeye") == 1.0  # No badge
        badges.add_badge("deadeye", BadgeTier.BRONZE)
        assert badges.tier_multiplier("deadeye") == pytest.approx(1.02)
        badges.add_badge("deadeye", BadgeTier.HALL_OF_FAME)
        assert badges.tier_multiplier("deadeye") == pytest.approx(1.10)

    def test_upgrade_badge(self):
        badges = PlayerBadges()
        badges.add_badge("clamps", BadgeTier.BRONZE)
        assert badges.upgrade_badge("clamps")
        assert badges.get_tier("clamps") == BadgeTier.SILVER

    def test_upgrade_hof_fails(self):
        badges = PlayerBadges()
        badges.add_badge("clamps", BadgeTier.HALL_OF_FAME)
        assert not badges.upgrade_badge("clamps")

    def test_upgrade_nonexistent_fails(self):
        badges = PlayerBadges()
        assert not badges.upgrade_badge("clamps")

    def test_remove_badge(self):
        badges = PlayerBadges()
        badges.add_badge("deadeye", BadgeTier.GOLD)
        badges.remove_badge("deadeye")
        assert not badges.has_badge("deadeye")

    def test_badges_in_category(self):
        badges = PlayerBadges()
        badges.add_badge("deadeye", BadgeTier.GOLD)
        badges.add_badge("catch_and_shoot", BadgeTier.SILVER)
        badges.add_badge("clamps", BadgeTier.BRONZE)

        shooting = badges.badges_in_category(BadgeCategory.SHOOTING)
        assert len(shooting) == 2
        assert "deadeye" in shooting
        assert "clamps" not in shooting

    def test_total_tier_points(self):
        badges = PlayerBadges()
        badges.add_badge("deadeye", BadgeTier.GOLD)  # 3
        badges.add_badge("clamps", BadgeTier.SILVER)  # 2
        assert badges.total_tier_points() == 5
