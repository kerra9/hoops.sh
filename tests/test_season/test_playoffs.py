"""Tests for the playoff bracket system."""

from hoops_sim.season.playoffs import (
    PlayoffBracket,
    PlayoffRound,
    PlayoffSeries,
    create_playoff_bracket,
)


class TestPlayoffSeries:
    def test_initial_state(self):
        series = PlayoffSeries(
            series_id=1, round=PlayoffRound.FIRST_ROUND,
            conference="East", higher_seed_id=1, lower_seed_id=8,
        )
        assert len(series.games) == 7
        assert not series.is_over
        assert series.winner_id is None

    def test_home_court_pattern(self):
        series = PlayoffSeries(
            series_id=1, round=PlayoffRound.FIRST_ROUND,
            conference="East", higher_seed_id=1, lower_seed_id=8,
        )
        # Games 1,2 at higher seed home
        assert series.games[0].home_team_id == 1
        assert series.games[1].home_team_id == 1
        # Games 3,4 at lower seed home
        assert series.games[2].home_team_id == 8
        assert series.games[3].home_team_id == 8

    def test_record_game_and_win(self):
        series = PlayoffSeries(
            series_id=1, round=PlayoffRound.FIRST_ROUND,
            conference="East", higher_seed_id=1, lower_seed_id=8,
        )
        # Higher seed (1) wins all games regardless of home/away
        for i in range(4):
            game = series.games[i]
            if game.home_team_id == 1:
                series.record_game(i + 1, home_score=110, away_score=100)
            else:
                series.record_game(i + 1, home_score=100, away_score=110)

        assert series.higher_seed_wins == 4
        assert series.is_over
        assert series.winner_id == 1

    def test_series_goes_to_seven(self):
        series = PlayoffSeries(
            series_id=1, round=PlayoffRound.FIRST_ROUND,
            conference="East", higher_seed_id=1, lower_seed_id=8,
        )
        # Higher seed wins games 1,3,5,7; lower seed wins 2,4,6
        pattern = [1, 8, 1, 8, 1, 8, 1]  # Winner by game
        for i in range(7):
            game = series.games[i]
            winner = pattern[i]
            if game.home_team_id == winner:
                series.record_game(i + 1, home_score=110, away_score=100)
            else:
                series.record_game(i + 1, home_score=100, away_score=110)

        assert series.is_over
        assert series.higher_seed_wins == 4
        assert series.lower_seed_wins == 3

    def test_series_score_display(self):
        series = PlayoffSeries(
            series_id=1, round=PlayoffRound.FIRST_ROUND,
            conference="East", higher_seed_id=1, lower_seed_id=8,
            higher_seed_name="BOS", lower_seed_name="MIA",
        )
        series.record_game(1, 110, 100)
        assert "BOS 1" in series.series_score
        assert "MIA 0" in series.series_score


class TestCreatePlayoffBracket:
    def test_creates_8_first_round_series(self):
        east = [(i, f"East{i}") for i in range(1, 9)]
        west = [(i + 10, f"West{i}") for i in range(1, 9)]
        bracket = create_playoff_bracket(east, west)

        first_round = bracket.get_series_for_round(PlayoffRound.FIRST_ROUND)
        assert len(first_round) == 8

    def test_seeding_matchups(self):
        east = [(i, f"E{i}") for i in range(1, 9)]
        west = [(i + 10, f"W{i}") for i in range(1, 9)]
        bracket = create_playoff_bracket(east, west)

        first_round = bracket.get_series_for_round(PlayoffRound.FIRST_ROUND)
        east_series = [s for s in first_round if s.conference == "East"]

        # 1 vs 8
        matchup_1v8 = [s for s in east_series if s.higher_seed_num == 1]
        assert len(matchup_1v8) == 1
        assert matchup_1v8[0].lower_seed_num == 8

    def test_advance_round(self):
        east = [(i, f"E{i}") for i in range(1, 9)]
        west = [(i + 10, f"W{i}") for i in range(1, 9)]
        bracket = create_playoff_bracket(east, west)

        # Simulate all first round series (higher seed sweeps)
        for series in bracket.get_series_for_round(PlayoffRound.FIRST_ROUND):
            for g in range(4):
                game = series.games[g]
                if game.home_team_id == series.higher_seed_id:
                    series.record_game(g + 1, home_score=110, away_score=100)
                else:
                    series.record_game(g + 1, home_score=100, away_score=110)

        # All first round series should be over
        for s in bracket.get_series_for_round(PlayoffRound.FIRST_ROUND):
            assert s.is_over, f"Series {s.series_id} not over: {s.series_score}"

        # Advance to second round
        assert bracket.advance_round()
        semis = bracket.get_series_for_round(PlayoffRound.CONFERENCE_SEMIS)
        assert len(semis) == 4  # 2 per conference
