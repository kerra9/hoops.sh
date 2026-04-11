"""Tests for the ProseComposer."""

import random

from hoops_sim.broadcast.composer.prose_composer import ProseComposer
from hoops_sim.events.game_events import (
    ActionChainResult,
    ClockSnapshot,
    MomentumSnapshot,
    MoveResult,
    PlayerRef,
    PossessionResult,
    ScoreSnapshot,
    ShotResult,
    TurnoverResult,
    FoulResult,
    ViolationResult,
    ReboundResult,
    DriveResult,
    ScreenResult,
    PassResult,
)


def _make_refs():
    handler = PlayerRef(id=1, name="Marcus Williams", team="Celtics", jersey=7)
    defender = PlayerRef(id=2, name="Jaylen Thompson", team="Knicks", jersey=24)
    return handler, defender


class TestProseComposer:
    def setup_method(self):
        self.composer = ProseComposer(rng=random.Random(42))

    def _base_possession(self, **kwargs):
        handler, defender = _make_refs()
        defaults = dict(
            ball_handler=handler,
            primary_defender=defender,
            offensive_team="Celtics",
            defensive_team="Knicks",
            clock=ClockSnapshot(quarter=2, game_clock=400.0),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=50, away_score=48,
                home_score_after=52, away_score_after=48,
            ),
            momentum=MomentumSnapshot(),
        )
        defaults.update(kwargs)
        return PossessionResult(**defaults)

    def test_condensed_made_shot(self):
        p = self._base_possession(
            shot=ShotResult(made=True, points=2, shot_type="mid_range"),
        )
        text = self.composer.compose(p, 0.1)
        assert "Williams" in text
        assert text  # Non-empty

    def test_condensed_miss(self):
        p = self._base_possession(
            shot=ShotResult(made=False, points=0),
        )
        text = self.composer.compose(p, 0.1)
        assert "misses" in text.lower() or "miss" in text.lower() or "Williams" in text

    def test_full_narration_made_three(self):
        p = self._base_possession(
            shot=ShotResult(
                shooter=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
                made=True, points=3, shot_type="pull_up_three",
            ),
        )
        text = self.composer.compose(p, 0.8)
        assert len(text) > 20  # Should be substantial narration
        assert "Williams" in text

    def test_full_narration_dunk(self):
        p = self._base_possession(
            shot=ShotResult(
                shooter=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
                made=True, points=2, is_dunk=True,
            ),
        )
        text = self.composer.compose(p, 0.85)
        assert "Williams" in text
        # Should have some excitement
        assert "!" in text or "dunk" in text.lower() or "slam" in text.lower()

    def test_turnover_narration(self):
        p = self._base_possession(
            turnover=TurnoverResult(
                turnover_type="steal",
                stealer=PlayerRef(id=3, name="Devin Barnes", team="Knicks"),
            ),
        )
        text = self.composer.compose(p, 0.6)
        assert "Barnes" in text or "steal" in text.lower() or "Stolen" in text

    def test_foul_narration(self):
        p = self._base_possession(
            foul=FoulResult(
                fouler=PlayerRef(id=2, name="Jaylen Thompson", team="Knicks"),
                fouled_player=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
                free_throws_awarded=2,
                free_throws_made=1,
                fouler_foul_count=3,
            ),
        )
        text = self.composer.compose(p, 0.5)
        assert "Thompson" in text or "foul" in text.lower()

    def test_action_chain_narration(self):
        handler, defender = _make_refs()
        p = self._base_possession(
            action_chain=ActionChainResult(
                player=handler,
                defender=defender,
                moves=[
                    MoveResult(move_type="crossover", success=True, defender_reaction="bites", separation_gained=1.5),
                    MoveResult(move_type="hesitation", success=True, defender_reaction="recovers", separation_gained=0.5),
                ],
                total_separation=2.0,
                outcome="separation",
            ),
            shot=ShotResult(made=True, points=2),
        )
        text = self.composer.compose(p, 0.7)
        assert len(text) > 30

    def test_violation_narration(self):
        p = self._base_possession(
            violation=ViolationResult(violation_type="shot_clock"),
        )
        text = self.composer.compose(p, 0.4)
        assert "shot clock" in text.lower() or "violation" in text.lower()

    def test_no_repeated_templates(self):
        """Two identical possessions should produce different text."""
        texts = set()
        for _ in range(10):
            p = self._base_possession(
                shot=ShotResult(
                    shooter=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
                    made=True, points=3,
                ),
            )
            text = self.composer.compose(p, 0.7)
            texts.add(text)
        # Should have some variation (at least 2 different outputs)
        assert len(texts) >= 2

    def test_score_line_in_output(self):
        p = self._base_possession(
            shot=ShotResult(made=True, points=2),
        )
        text = self.composer.compose(p, 0.4)
        # Score line should appear somewhere
        assert "Celtics" in text or "Knicks" in text or "52" in text
