"""Tests for the history and records tracking system."""

from hoops_sim.history.records import HistoryTracker, GameRecord


class TestHistoryTracker:
    def test_record_game(self):
        tracker = HistoryTracker()
        rec = tracker.record_game(
            season_year=2025, day=1,
            home_team_id=1, away_team_id=2,
            home_team_name="BOS", away_team_name="LAL",
            home_score=110, away_score=105,
            top_scorer_name="Tatum", top_scorer_points=35,
        )
        assert rec.game_id == 1
        assert rec.winner_id == 1
        assert len(tracker.game_history) == 1

    def test_franchise_records_updated(self):
        tracker = HistoryTracker()
        tracker.record_game(
            season_year=2025, day=1,
            home_team_id=1, away_team_id=2,
            home_team_name="BOS", away_team_name="LAL",
            home_score=150, away_score=100,
            top_scorer_name="Star", top_scorer_points=60,
        )
        fr = tracker.franchise_records[1]
        assert fr.highest_score == 150
        assert fr.individual_high_points == 60

    def test_season_end_tracking(self):
        tracker = HistoryTracker()
        tracker.record_season_end(1, "BOS", 60, 22, 2025, is_champion=True)
        fr = tracker.franchise_records[1]
        assert fr.championships == 1
        assert fr.best_season_wins == 60
        assert 2025 in fr.championship_years

    def test_games_for_team(self):
        tracker = HistoryTracker()
        tracker.record_game(2025, 1, 1, 2, "A", "B", 100, 90)
        tracker.record_game(2025, 2, 3, 1, "C", "A", 95, 100)
        tracker.record_game(2025, 3, 2, 3, "B", "C", 105, 100)

        team1_games = tracker.games_for_team(1)
        assert len(team1_games) == 2

    def test_score_line(self):
        rec = GameRecord(
            home_team_id=1, away_team_id=2,
            home_team_name="BOS", away_team_name="LAL",
            home_score=110, away_score=105,
        )
        assert "LAL 105 @ BOS 110" == rec.score_line
