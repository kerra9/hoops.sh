"""Tests for standings system."""

from __future__ import annotations

import pytest

from hoops_sim.season.standings import Standings, TeamRecord


class TestTeamRecord:
    def test_initial(self):
        r = TeamRecord()
        assert r.games_played == 0
        assert r.win_pct == 0.0

    def test_record_win(self):
        r = TeamRecord()
        r.record_win(is_home=True, is_conference=True, is_division=True, pts_for=110, pts_against=100)
        assert r.wins == 1
        assert r.home_wins == 1
        assert r.conference_wins == 1
        assert r.point_diff == 10

    def test_record_loss(self):
        r = TeamRecord()
        r.record_loss(is_home=False, is_conference=True, is_division=False, pts_for=95, pts_against=105)
        assert r.losses == 1
        assert r.away_losses == 1

    def test_win_pct(self):
        r = TeamRecord(wins=41, losses=41)
        assert r.win_pct == pytest.approx(0.5)

    def test_streak(self):
        r = TeamRecord()
        r.record_win(True, True, True, 100, 90)
        r.record_win(True, True, True, 105, 95)
        assert r.streak == 2
        r.record_loss(True, True, True, 90, 100)
        assert r.streak == -1

    def test_display(self):
        r = TeamRecord(wins=50, losses=32)
        assert r.record_display == "50-32"


class TestStandings:
    def test_add_team(self):
        s = Standings()
        s.add_team(1, "Lakers", "West", "Pacific")
        assert s.get_record(1).team_name == "Lakers"

    def test_conference_standings(self):
        s = Standings()
        s.add_team(1, "Lakers", "West", "Pacific")
        s.add_team(2, "Celtics", "East", "Atlantic")
        s.add_team(3, "Nuggets", "West", "Northwest")

        west = s.conference_standings("West")
        assert len(west) == 2

    def test_sorted_by_win_pct(self):
        s = Standings()
        s.add_team(1, "Bad Team", "West", "Pacific")
        s.add_team(2, "Good Team", "West", "Pacific")
        s.get_record(1).wins = 20
        s.get_record(1).losses = 62
        s.get_record(2).wins = 60
        s.get_record(2).losses = 22
        
        standings = s.conference_standings("West")
        assert standings[0].team_name == "Good Team"

    def test_playoff_teams(self):
        s = Standings()
        for i in range(15):
            s.add_team(i, f"Team {i}", "East", "Atlantic")
            s.get_record(i).wins = 82 - i * 5
            s.get_record(i).losses = i * 5
        
        playoff = s.playoff_teams("East", count=8)
        assert len(playoff) == 8
        assert playoff[0].wins > playoff[7].wins
