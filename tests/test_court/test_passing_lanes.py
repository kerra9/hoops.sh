"""Tests for passing lane analysis."""

from __future__ import annotations

import pytest

from hoops_sim.court.passing_lanes import analyze_passing_lane, point_to_segment_distance
from hoops_sim.physics.vec import Vec2


class TestPointToSegmentDistance:
    def test_point_on_segment(self):
        d = point_to_segment_distance(Vec2(5, 0), Vec2(0, 0), Vec2(10, 0))
        assert d == pytest.approx(0.0)

    def test_point_perpendicular(self):
        d = point_to_segment_distance(Vec2(5, 3), Vec2(0, 0), Vec2(10, 0))
        assert d == pytest.approx(3.0)

    def test_point_past_end(self):
        d = point_to_segment_distance(Vec2(15, 0), Vec2(0, 0), Vec2(10, 0))
        assert d == pytest.approx(5.0)


class TestAnalyzePassingLane:
    def test_wide_open(self):
        result = analyze_passing_lane(
            passer_pos=Vec2(50, 25),
            receiver_pos=Vec2(70, 25),
            defender_positions=[Vec2(80, 10)],  # Far from lane
        )
        assert result.open
        assert result.quality > 0.8
        assert result.interception_risk < 0.1

    def test_blocked(self):
        result = analyze_passing_lane(
            passer_pos=Vec2(50, 25),
            receiver_pos=Vec2(70, 25),
            defender_positions=[Vec2(60, 25)],  # Directly in the lane
        )
        assert not result.open
        assert result.quality < 0.5
        assert result.interception_risk > 0.05

    def test_no_defenders(self):
        result = analyze_passing_lane(
            passer_pos=Vec2(50, 25),
            receiver_pos=Vec2(70, 25),
            defender_positions=[],
        )
        assert result.open
        assert result.quality == 1.0

    def test_multiple_defenders(self):
        result = analyze_passing_lane(
            passer_pos=Vec2(50, 25),
            receiver_pos=Vec2(70, 25),
            defender_positions=[Vec2(58, 26), Vec2(62, 24)],
        )
        assert result.closest_defender_distance < 3.0
