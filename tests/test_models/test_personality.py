"""Tests for player personality model."""

from __future__ import annotations

import pytest

from hoops_sim.models.personality import PlayerPersonality


class TestPlayerPersonality:
    def test_defaults(self):
        p = PlayerPersonality()
        assert 0.0 <= p.ego <= 1.0
        assert 0.0 <= p.competitiveness <= 1.0

    def test_high_ego(self):
        p = PlayerPersonality(ego=0.8)
        assert p.is_high_ego()
        p2 = PlayerPersonality(ego=0.3)
        assert not p2.is_high_ego()

    def test_volatile(self):
        p = PlayerPersonality(temperament=0.2)
        assert p.is_volatile()
        p2 = PlayerPersonality(temperament=0.7)
        assert not p2.is_volatile()

    def test_team_first(self):
        p = PlayerPersonality(ego=0.2, sociability=0.8)
        assert p.is_team_first()
        p2 = PlayerPersonality(ego=0.8, sociability=0.3)
        assert not p2.is_team_first()

    def test_chemistry_impact(self):
        good = PlayerPersonality(
            sociability=0.9, professionalism=0.9,
            locker_room_presence=0.9, coachable=0.9,
            temperament=0.9, ego=0.1, mentor_willing=0.8,
        )
        bad = PlayerPersonality(
            sociability=0.1, professionalism=0.1,
            locker_room_presence=0.1, coachable=0.1,
            temperament=0.1, ego=0.9, social_media_active=0.9,
        )
        assert good.chemistry_impact() > bad.chemistry_impact()

    def test_tech_foul_tendency(self):
        calm = PlayerPersonality(temperament=0.9, ego=0.1, professionalism=0.9)
        volatile = PlayerPersonality(temperament=0.1, ego=0.9, competitiveness=0.9)
        assert volatile.tech_foul_tendency() > calm.tech_foul_tendency()
        assert calm.tech_foul_tendency() >= 0.0
