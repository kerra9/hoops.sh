"""Tests for PnR coverage system."""

from __future__ import annotations

import pytest

from hoops_sim.defense.pnr_coverage import PnRCoverageType, evaluate_pnr_coverage


class TestPnRCoverage:
    def test_drop_gives_mid_range(self):
        result = evaluate_pnr_coverage(
            coverage=PnRCoverageType.DROP,
            handler_ball_handle=85, handler_three_point=80,
            screener_roll_rating=75, screener_can_shoot=False,
            defender_lateral=70, big_defender_perimeter=50,
        )
        assert result.mid_range_open

    def test_switch_creates_mismatch(self):
        result = evaluate_pnr_coverage(
            coverage=PnRCoverageType.SWITCH,
            handler_ball_handle=90, handler_three_point=85,
            screener_roll_rating=80, screener_can_shoot=False,
            defender_lateral=75, big_defender_perimeter=40,
        )
        assert result.mismatch_created

    def test_blitz_opens_roller_and_three(self):
        result = evaluate_pnr_coverage(
            coverage=PnRCoverageType.BLITZ,
            handler_ball_handle=70, handler_three_point=75,
            screener_roll_rating=80, screener_can_shoot=False,
            defender_lateral=75, big_defender_perimeter=55,
        )
        assert result.roller_open
        assert result.three_open

    def test_veer_gives_three(self):
        result = evaluate_pnr_coverage(
            coverage=PnRCoverageType.VEER,
            handler_ball_handle=80, handler_three_point=85,
            screener_roll_rating=60, screener_can_shoot=False,
            defender_lateral=70, big_defender_perimeter=50,
        )
        assert result.three_open

    def test_all_coverages_valid(self):
        for coverage in PnRCoverageType:
            result = evaluate_pnr_coverage(
                coverage=coverage,
                handler_ball_handle=75, handler_three_point=75,
                screener_roll_rating=70, screener_can_shoot=True,
                defender_lateral=70, big_defender_perimeter=55,
            )
            assert result.coverage_used == coverage
