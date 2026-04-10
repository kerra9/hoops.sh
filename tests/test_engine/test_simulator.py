"""Tests for the GameSimulator -- the core basketball simulation engine."""

from __future__ import annotations

import pytest

from hoops_sim.data.generator import generate_roster
from hoops_sim.engine.simulator import GameSimulator, GameResult
from hoops_sim.models.player import Player, Position
from hoops_sim.models.team import Team
from hoops_sim.utils.rng import SeededRNG


def _make_team(team_id: int, city: str, name: str, seed: int = 42) -> Team:
    """Create a test team with a generated roster."""
    rng = SeededRNG(seed=seed)
    roster = generate_roster(rng)
    return Team(
        id=team_id,
        city=city,
        name=name,
        abbreviation=name[:3].upper(),
        conference="East",
        division="Atlantic",
        roster=roster,
    )


@pytest.fixture
def home_team() -> Team:
    return _make_team(1, "Boston", "Celtics", seed=100)


@pytest.fixture
def away_team() -> Team:
    return _make_team(2, "Los Angeles", "Lakers", seed=200)


class TestGameSimulatorInit:
    def test_creates_simulator(self, home_team, away_team):
        sim = GameSimulator(home_team=home_team, away_team=away_team, seed=42)
        assert sim.home_team is home_team
        assert sim.away_team is away_team
        assert not sim.is_game_over

    def test_court_state_initialized(self, home_team, away_team):
        sim = GameSimulator(home_team=home_team, away_team=away_team, seed=42)
        assert len(sim.court.home_on_court) == 5
        assert len(sim.court.away_on_court) == 5

    def test_stats_initialized_for_all_players(self, home_team, away_team):
        sim = GameSimulator(home_team=home_team, away_team=away_team, seed=42)
        for p in home_team.roster:
            stats = sim.home_stats.get_player(p.id)
            assert stats is not None
        for p in away_team.roster:
            stats = sim.away_stats.get_player(p.id)
            assert stats is not None


class TestGameSimulatorFullGame:
    def test_simulate_produces_valid_scores(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        # Scores should be in realistic NBA range
        assert result.home_score >= 50, f"Home score too low: {result.home_score}"
        assert result.away_score >= 50, f"Away score too low: {result.away_score}"
        assert result.home_score <= 180, f"Home score too high: {result.home_score}"
        assert result.away_score <= 180, f"Away score too high: {result.away_score}"

    def test_game_is_not_tied(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()
        assert result.home_score != result.away_score, "Game ended in a tie"

    def test_scores_match_stats(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        # Sum of player points should match team score
        home_player_points = sum(
            ps.points for ps in result.home_stats.player_stats.values()
        )
        away_player_points = sum(
            ps.points for ps in result.away_stats.player_stats.values()
        )
        assert home_player_points == result.home_score
        assert away_player_points == result.away_score

    def test_deterministic_with_same_seed(self, home_team, away_team):
        sim1 = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result1 = sim1.simulate_full_game()

        sim2 = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result2 = sim2.simulate_full_game()

        assert result1.home_score == result2.home_score
        assert result1.away_score == result2.away_score

    def test_different_seeds_different_results(self, home_team, away_team):
        sim1 = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result1 = sim1.simulate_full_game()

        sim2 = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=999,
            narrate=False,
        )
        result2 = sim2.simulate_full_game()

        # Very unlikely to get same scores with different seeds
        scores_differ = (
            result1.home_score != result2.home_score
            or result1.away_score != result2.away_score
        )
        assert scores_differ, "Different seeds produced identical results"

    def test_players_accumulate_stats(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        # At least some players should have field goal attempts
        home_fga = sum(ps.fga for ps in result.home_stats.player_stats.values())
        away_fga = sum(ps.fga for ps in result.away_stats.player_stats.values())
        assert home_fga > 30, f"Home FGA too low: {home_fga}"
        assert away_fga > 30, f"Away FGA too low: {away_fga}"

    def test_fg_pct_is_realistic(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        home_fg_pct = result.home_stats.team_fg_pct()
        away_fg_pct = result.away_stats.team_fg_pct()

        # FG% should be in a plausible range (generated rosters can skew high)
        assert 0.25 <= home_fg_pct <= 0.75, f"Home FG%: {home_fg_pct:.3f}"
        assert 0.25 <= away_fg_pct <= 0.75, f"Away FG%: {away_fg_pct:.3f}"

    def test_total_possessions_reasonable(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        # NBA games have ~200 total possessions (100 per team)
        assert result.total_possessions > 100, (
            f"Too few possessions: {result.total_possessions}"
        )
        assert result.total_possessions < 400, (
            f"Too many possessions: {result.total_possessions}"
        )


class TestGameSimulatorStep:
    def test_step_returns_events(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=True,
        )
        # Run enough steps to get some events
        all_events = []
        for _ in range(5000):
            events = sim.step()
            all_events.extend(events)
            if sim.is_game_over:
                break

        assert len(all_events) > 0, "No events produced during stepping"

    def test_step_advances_game(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        initial_score = sim.game_state.score.home + sim.game_state.score.away

        # Step many times
        for _ in range(10000):
            sim.step()
            if sim.is_game_over:
                break

        final_score = sim.game_state.score.home + sim.game_state.score.away
        assert final_score > initial_score, "Score didn't advance"


class TestNarration:
    def test_narration_events_have_text(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=True,
        )
        result = sim.simulate_full_game()

        narrated = [e for e in result.events if e.narration is not None]
        assert len(narrated) > 10, f"Too few narration events: {len(narrated)}"

        for event in narrated[:10]:
            assert event.narration.text, "Empty narration text"

    def test_no_narration_when_disabled(self, home_team, away_team):
        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        result = sim.simulate_full_game()

        narrated = [e for e in result.events if e.narration is not None]
        assert len(narrated) == 0, "Narration events when narration disabled"
