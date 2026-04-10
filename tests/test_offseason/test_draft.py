"""Tests for the NBA Draft system."""

from hoops_sim.offseason.draft import (
    generate_draft_class,
    determine_draft_order,
    execute_draft,
)
from hoops_sim.utils.rng import SeededRNG


class TestDraftClass:
    def test_generates_correct_count(self):
        rng = SeededRNG(seed=42)
        prospects = generate_draft_class(rng, num_prospects=60)
        assert len(prospects) == 60

    def test_top_prospects_rated_higher(self):
        rng = SeededRNG(seed=42)
        prospects = generate_draft_class(rng, num_prospects=30)
        top_5_avg = sum(p.player.overall for p in prospects[:5]) / 5
        last_5_avg = sum(p.player.overall for p in prospects[-5:]) / 5
        assert top_5_avg > last_5_avg

    def test_prospects_are_rookies(self):
        rng = SeededRNG(seed=42)
        prospects = generate_draft_class(rng, num_prospects=10)
        for p in prospects:
            assert p.player.years_pro == 0

    def test_scouting_info_populated(self):
        rng = SeededRNG(seed=42)
        prospects = generate_draft_class(rng, num_prospects=5)
        for p in prospects:
            assert p.scout_grade
            assert p.comparison
            assert len(p.strengths) > 0


class TestDraftOrder:
    def test_lottery_teams_first(self):
        records = [
            (1, "Team1", 20, 62),  # Bad record
            (2, "Team2", 55, 27),  # Good record (playoff)
            (3, "Team3", 30, 52),  # Mediocre
        ]
        order = determine_draft_order(records, {2}, SeededRNG(seed=42))
        # Non-playoff teams should pick before playoff teams
        first_pick_id = order[0][0]
        assert first_pick_id in (1, 3)


class TestExecuteDraft:
    def test_all_picks_assigned(self):
        rng = SeededRNG(seed=42)
        prospects = generate_draft_class(rng, num_prospects=60)
        order = [(i, f"Team{i}") for i in range(1, 31)]
        result = execute_draft(order, prospects)
        assert len(result.picks) == 30
        for pick in result.picks:
            assert pick.player is not None
