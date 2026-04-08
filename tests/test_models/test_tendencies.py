"""Tests for player tendencies."""

from __future__ import annotations

import pytest

from hoops_sim.models.tendencies import PlayerTendencies


class TestPlayerTendencies:
    def test_defaults_valid(self):
        t = PlayerTendencies()
        assert t.validate()

    def test_validate_out_of_range(self):
        t = PlayerTendencies(shot_volume=1.5)
        assert not t.validate()

    def test_validate_negative(self):
        t = PlayerTendencies(drive_tendency=-0.1)
        assert not t.validate()

    def test_clamp_all(self):
        t = PlayerTendencies(shot_volume=1.5, drive_tendency=-0.5)
        t.clamp_all()
        assert t.shot_volume == 1.0
        assert t.drive_tendency == 0.0
        assert t.validate()

    def test_has_20_tendencies(self):
        t = PlayerTendencies()
        count = sum(1 for v in t.__dict__.values() if isinstance(v, (int, float)))
        assert count == 20

    def test_custom_values(self):
        t = PlayerTendencies(
            shot_volume=0.8,
            three_point_tendency=0.9,
            pass_first=0.2,
        )
        assert t.shot_volume == 0.8
        assert t.three_point_tendency == 0.9
        assert t.pass_first == 0.2
