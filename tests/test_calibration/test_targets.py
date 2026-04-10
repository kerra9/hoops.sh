"""Tests for calibration targets."""

from __future__ import annotations

import pytest

from hoops_sim.calibration.targets import (
    TEAM_TARGETS,
    CalibrationReport,
    CalibrationTarget,
)


class TestCalibrationTarget:
    def test_in_range_true(self):
        target = CalibrationTarget("ppg", 110.0, 95.0, 125.0)
        assert target.is_in_range(110.0) is True
        assert target.is_in_range(95.0) is True
        assert target.is_in_range(125.0) is True

    def test_in_range_false(self):
        target = CalibrationTarget("ppg", 110.0, 95.0, 125.0)
        assert target.is_in_range(94.9) is False
        assert target.is_in_range(125.1) is False

    def test_deviation(self):
        target = CalibrationTarget("ppg", 100.0, 90.0, 110.0)
        assert target.deviation(100.0) == 0.0
        assert abs(target.deviation(110.0) - 0.1) < 0.001

    def test_all_targets_have_valid_ranges(self):
        for target in TEAM_TARGETS:
            assert target.min_acceptable < target.nba_average < target.max_acceptable, (
                f"{target.name}: min={target.min_acceptable}, avg={target.nba_average}, "
                f"max={target.max_acceptable}"
            )


class TestCalibrationReport:
    def test_empty_report(self):
        report = CalibrationReport()
        assert report.pass_rate == 0.0
        assert report.targets_met == 0

    def test_add_passing_result(self):
        report = CalibrationReport(games_simulated=10)
        target = CalibrationTarget("ppg", 110.0, 95.0, 125.0)
        report.add_result("ppg", 108.0, target)
        assert report.targets_met == 1
        assert report.targets_total == 1
        assert report.pass_rate == 1.0

    def test_add_failing_result(self):
        report = CalibrationReport(games_simulated=10)
        target = CalibrationTarget("ppg", 110.0, 95.0, 125.0)
        report.add_result("ppg", 80.0, target)
        assert report.targets_met == 0
        assert report.pass_rate == 0.0

    def test_summary_format(self):
        report = CalibrationReport(games_simulated=50)
        target = CalibrationTarget("ppg", 110.0, 95.0, 125.0)
        report.add_result("ppg", 108.0, target)
        summary = report.summary()
        assert "1/1" in summary
        assert "50 games" in summary
