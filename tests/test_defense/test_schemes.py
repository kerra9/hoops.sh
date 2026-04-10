"""Tests for the defensive scheme system."""

from hoops_sim.defense.schemes import (
    DefensiveScheme,
    SCHEME_MODIFIERS,
    get_scheme_modifiers,
    select_defensive_scheme,
)


class TestSchemeModifiers:
    def test_all_schemes_have_modifiers(self):
        for scheme in DefensiveScheme:
            mods = get_scheme_modifiers(scheme)
            assert mods is not None

    def test_zone_saves_energy(self):
        man = get_scheme_modifiers(DefensiveScheme.MAN_TO_MAN)
        zone = get_scheme_modifiers(DefensiveScheme.ZONE_2_3)
        assert zone.energy_cost_mod < man.energy_cost_mod

    def test_press_generates_steals(self):
        press = get_scheme_modifiers(DefensiveScheme.FULL_COURT_PRESS)
        man = get_scheme_modifiers(DefensiveScheme.MAN_TO_MAN)
        assert press.steal_chance_mod > man.steal_chance_mod

    def test_drop_protects_rim(self):
        drop = get_scheme_modifiers(DefensiveScheme.DROP_COVERAGE)
        assert drop.interior_contest > 1.0
        assert drop.paint_vulnerability < 1.0


class TestSelectScheme:
    def test_three_point_threat_gets_3_2(self):
        scheme = select_defensive_scheme(
            opponent_three_pct=0.45,
            opponent_paint_points_pct=0.3,
            own_team_athleticism=60,
            score_diff=0,
            quarter=2,
            minutes_remaining=6.0,
        )
        assert scheme == DefensiveScheme.ZONE_3_2

    def test_paint_dominant_gets_2_3(self):
        scheme = select_defensive_scheme(
            opponent_three_pct=0.30,
            opponent_paint_points_pct=0.60,
            own_team_athleticism=60,
            score_diff=0,
            quarter=2,
            minutes_remaining=6.0,
        )
        assert scheme == DefensiveScheme.ZONE_2_3

    def test_big_deficit_triggers_press(self):
        scheme = select_defensive_scheme(
            opponent_three_pct=0.33,
            opponent_paint_points_pct=0.40,
            own_team_athleticism=70,
            score_diff=-20,
            quarter=4,
            minutes_remaining=6.0,
        )
        assert scheme == DefensiveScheme.FULL_COURT_PRESS
