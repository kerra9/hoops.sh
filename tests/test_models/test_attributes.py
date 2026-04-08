"""Tests for PlayerAttributes model."""

from __future__ import annotations

import pytest

from hoops_sim.models.attributes import (
    AthleticAttributes,
    DefensiveAttributes,
    FinishingAttributes,
    MentalAttributes,
    PlaymakingAttributes,
    PlayerAttributes,
    ReboundingAttributes,
    ShootingAttributes,
)


class TestShootingAttributes:
    def test_defaults(self):
        s = ShootingAttributes()
        assert s.close_shot == 50
        assert s.three_point == 50
        assert s.free_throw == 50
        assert s.shot_speed == 50


class TestPlayerAttributes:
    def test_defaults(self):
        attrs = PlayerAttributes()
        assert attrs.shooting.mid_range == 50
        assert attrs.finishing.layup == 50
        assert attrs.defense.steal == 50

    def test_overall(self):
        attrs = PlayerAttributes()
        ovr = attrs.overall()
        assert 40 <= ovr <= 60  # All 50s should be around 50

    def test_overall_high(self):
        attrs = PlayerAttributes(
            shooting=ShootingAttributes(
                close_shot=90, mid_range=90, three_point=90,
                free_throw=90, shot_iq=90, shot_consistency=90, shot_speed=85,
            ),
            finishing=FinishingAttributes(
                layup=90, standing_dunk=85, driving_dunk=88,
                draw_foul=85, acrobatic_finish=85, post_hook=80,
                post_fadeaway=80, post_moves=80,
            ),
            playmaking=PlaymakingAttributes(
                ball_handle=88, pass_accuracy=90, pass_vision=90,
                pass_iq=90, speed_with_ball=85, hands=85,
            ),
            defense=DefensiveAttributes(
                interior_defense=85, perimeter_defense=88,
                lateral_quickness=88, steal=85, block=80,
                defensive_iq=90, defensive_consistency=90,
                pick_dodger=85, help_defense_iq=88, on_ball_defense=88,
            ),
            rebounding=ReboundingAttributes(
                offensive_rebound=75, defensive_rebound=80, box_out=78,
            ),
            athleticism=AthleticAttributes(
                speed=88, acceleration=88, vertical_leap=85,
                strength=80, stamina=90, hustle=90, durability=85,
            ),
            mental=MentalAttributes(
                basketball_iq=95, clutch=90, composure=90,
                work_ethic=90, coachability=85, leadership=90,
                mentorship=80, motor=90,
            ),
        )
        ovr = attrs.overall()
        assert ovr >= 80

    def test_iter_all(self):
        attrs = PlayerAttributes()
        all_attrs = list(attrs.iter_all())
        assert len(all_attrs) >= 49  # 49 attributes across 7 categories

    def test_count(self):
        attrs = PlayerAttributes()
        assert attrs.count() >= 49

    def test_to_dict(self):
        attrs = PlayerAttributes()
        d = attrs.to_dict()
        assert "shooting" in d
        assert "defense" in d
        assert "mid_range" in d["shooting"]

    def test_get(self):
        attrs = PlayerAttributes()
        attrs.shooting.three_point = 85
        assert attrs.get("shooting", "three_point") == 85

    def test_get_invalid_category(self):
        attrs = PlayerAttributes()
        with pytest.raises(ValueError):
            attrs.get("invalid", "three_point")

    def test_get_invalid_attribute(self):
        attrs = PlayerAttributes()
        with pytest.raises(ValueError):
            attrs.get("shooting", "invalid_attr")
