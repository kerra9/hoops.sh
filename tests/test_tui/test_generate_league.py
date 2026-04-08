"""Tests for league generation functionality."""

from __future__ import annotations

import pytest

from hoops_sim.data.generator import generate_league
from hoops_sim.utils.rng import SeededRNG


def test_generate_league_default():
    """Generate a league with 30 teams."""
    rng = SeededRNG(seed=42)
    league = generate_league(num_teams=30, rng=rng)
    assert league.team_count() == 30
    assert len(league.teams) == 30


def test_generate_league_small():
    """Generate a smaller league."""
    rng = SeededRNG(seed=42)
    league = generate_league(num_teams=6, rng=rng)
    assert league.team_count() == 6


def test_generate_league_teams_have_rosters():
    """Each team should have a full roster."""
    rng = SeededRNG(seed=42)
    league = generate_league(num_teams=6, rng=rng)
    for team in league.teams:
        assert len(team.roster) == 15
        assert team.city != ""
        assert team.name != ""
        assert team.abbreviation != ""


def test_generate_league_deterministic():
    """Same seed should produce same league."""
    league1 = generate_league(num_teams=6, rng=SeededRNG(seed=123))
    league2 = generate_league(num_teams=6, rng=SeededRNG(seed=123))

    for t1, t2 in zip(league1.teams, league2.teams):
        assert t1.full_name == t2.full_name
        assert len(t1.roster) == len(t2.roster)
        for p1, p2 in zip(t1.roster, t2.roster):
            assert p1.full_name == p2.full_name
            assert p1.overall == p2.overall


def test_standings_record_game():
    """Standings.record_game updates both team records."""
    from hoops_sim.season.standings import Standings

    standings = Standings()
    standings.add_team(1, "Team A", "East", "Atlantic")
    standings.add_team(2, "Team B", "East", "Atlantic")

    standings.record_game(1, 2, 110, 95, is_home_win=True, is_conference=True, is_division=True)

    rec_a = standings.get_record(1)
    rec_b = standings.get_record(2)

    assert rec_a.wins == 1
    assert rec_a.losses == 0
    assert rec_b.wins == 0
    assert rec_b.losses == 1
    assert rec_a.points_for == 110
    assert rec_a.points_against == 95


def test_attribute_averages():
    """PlayerAttributes category averages work."""
    from hoops_sim.models.attributes import PlayerAttributes

    attrs = PlayerAttributes()
    # All defaults are 50
    assert attrs.shooting_avg() == 50
    assert attrs.finishing_avg() == 50
    assert attrs.defense_avg() == 50
    assert attrs.rebounding_avg() == 50
    assert attrs.athleticism_avg() == 50
    assert attrs.mental_avg() == 50
    assert attrs.playmaking_avg() == 50
