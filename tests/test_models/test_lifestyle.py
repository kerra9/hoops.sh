"""Tests for player lifestyle model."""

from __future__ import annotations

import pytest

from hoops_sim.models.lifestyle import PlayerLifestyle


class TestPlayerLifestyle:
    def test_defaults(self):
        ls = PlayerLifestyle()
        assert 0.0 <= ls.sleep_quality <= 1.0

    def test_daily_recovery_modifier(self):
        good = PlayerLifestyle(sleep_quality=1.0, nutrition=1.0, personal_life=1.0)
        bad = PlayerLifestyle(sleep_quality=0.0, nutrition=0.0, personal_life=0.0)
        assert good.daily_recovery_modifier() > bad.daily_recovery_modifier()
        assert good.daily_recovery_modifier() <= 1.0
        assert bad.daily_recovery_modifier() >= 0.5

    def test_game_day_focus(self):
        focused = PlayerLifestyle(media_pressure=0.2, personal_life=0.9)
        distracted = PlayerLifestyle(media_pressure=0.9, personal_life=0.2)
        assert focused.game_day_focus() >= distracted.game_day_focus()
        assert distracted.game_day_focus() == 0.90

    def test_morale_modifier(self):
        happy = PlayerLifestyle(endorsements=0.9, personal_life=0.9, media_pressure=0.1)
        unhappy = PlayerLifestyle(endorsements=0.0, personal_life=0.1, media_pressure=0.9)
        assert happy.morale_modifier() > unhappy.morale_modifier()

    def test_injury_risk_modifier(self):
        healthy = PlayerLifestyle(sleep_quality=0.9, nutrition=0.9)
        unhealthy = PlayerLifestyle(sleep_quality=0.3, nutrition=0.3)
        assert unhealthy.injury_risk_modifier() > healthy.injury_risk_modifier()
        assert healthy.injury_risk_modifier() == pytest.approx(1.0)

    def test_weight_change(self):
        good_diet = PlayerLifestyle(nutrition=0.9)
        bad_diet = PlayerLifestyle(nutrition=0.1)
        assert good_diet.weight_change_tendency() < 0  # Losing weight
        assert bad_diet.weight_change_tendency() > 0  # Gaining weight
