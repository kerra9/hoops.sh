"""Tests for season stats aggregation."""

from hoops_sim.models.season_stats import PlayerSeasonStats, TeamSeasonStats, SeasonStatsTracker
from hoops_sim.models.stats import PlayerGameStats, TeamGameStats


class TestPlayerSeasonStats:
    def test_add_game_accumulates(self):
        ss = PlayerSeasonStats(player_id=1, player_name="Test")
        gs = PlayerGameStats(player_id=1, points=20, fgm=8, fga=15, three_pm=2, three_pa=5)
        ss.add_game(gs)
        assert ss.games_played == 1
        assert ss.total_points == 20
        assert ss.ppg == 20.0

    def test_averages_across_games(self):
        ss = PlayerSeasonStats(player_id=1, player_name="Test")
        ss.add_game(PlayerGameStats(player_id=1, points=30, fgm=12, fga=20))
        ss.add_game(PlayerGameStats(player_id=1, points=10, fgm=4, fga=10))
        assert ss.games_played == 2
        assert ss.ppg == 20.0
        assert ss.fg_pct == 16 / 30

    def test_stat_line(self):
        ss = PlayerSeasonStats(player_id=1, player_name="Test", total_points=500, games_played=25)
        ss.total_oreb = 25
        ss.total_dreb = 125
        ss.total_assists = 100
        assert "20.0 PPG" in ss.stat_line()
        assert "6.0 RPG" in ss.stat_line()
        assert "4.0 APG" in ss.stat_line()


class TestSeasonStatsTracker:
    def test_record_game(self):
        tracker = SeasonStatsTracker()
        home = TeamGameStats(team_id=1, team_name="Home", points=110)
        home.add_player(10, "Player A")
        home.get_player(10).record_made_shot(is_three=True)

        away = TeamGameStats(team_id=2, team_name="Away", points=100)
        tracker.record_game(1, "Home", 2, "Away", home, away)

        assert 1 in tracker.team_stats
        assert 2 in tracker.team_stats
        assert tracker.team_stats[1].games_played == 1

    def test_league_leaders(self):
        tracker = SeasonStatsTracker()
        for _ in range(6):
            home = TeamGameStats(team_id=1, team_name="Home", points=100)
            home.add_player(10, "Star")
            home.get_player(10).points = 30
            home.get_player(10).fgm = 12
            home.get_player(10).fga = 20

            away = TeamGameStats(team_id=2, team_name="Away", points=90)
            away.add_player(20, "Role")
            away.get_player(20).points = 15
            away.get_player(20).fgm = 6
            away.get_player(20).fga = 12

            tracker.record_game(1, "Home", 2, "Away", home, away)

        leaders = tracker.league_leaders("ppg")
        assert len(leaders) >= 1
        assert leaders[0].player_name == "Star"
