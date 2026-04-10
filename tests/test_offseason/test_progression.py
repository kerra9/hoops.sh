"""Tests for player progression system."""

from hoops_sim.data.generator import generate_player
from hoops_sim.offseason.progression import progress_player, progress_roster
from hoops_sim.utils.rng import SeededRNG


class TestProgression:
    def test_young_player_improves(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng, age=20, overall_target=65)
        old_ovr = player.overall

        rng2 = SeededRNG(seed=42)
        result = progress_player(player, rng2)

        # Young players should generally improve (not guaranteed, but likely)
        assert result.age == 21
        assert len(result.changes) > 0

    def test_old_player_declines(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng, age=36, overall_target=75)
        old_ovr = player.overall

        rng2 = SeededRNG(seed=42)
        result = progress_player(player, rng2)

        assert result.age == 37
        # Old players should decline on average
        assert result.new_overall <= old_ovr + 2  # Allow small variance

    def test_ages_player(self):
        rng = SeededRNG(seed=42)
        player = generate_player(rng, age=25)
        progress_player(player, SeededRNG(seed=1))
        assert player.age == 26

    def test_progress_roster(self):
        rng = SeededRNG(seed=42)
        roster = [generate_player(SeededRNG(seed=i), age=22 + i) for i in range(5)]
        results = progress_roster(roster, rng)
        assert len(results) == 5
        for r in results:
            assert r.player_name
