"""Tests for the VerbosityScorer."""

from hoops_sim.broadcast.pacing.verbosity_scorer import VerbosityLevel, VerbosityScorer
from hoops_sim.events.game_events import (
    ClockSnapshot,
    MomentumSnapshot,
    PossessionResult,
    ScoreSnapshot,
    ShotResult,
    TurnoverResult,
)


class TestVerbosityScorer:
    def setup_method(self):
        self.scorer = VerbosityScorer()

    def _make_possession(self, **kwargs):
        defaults = dict(
            clock=ClockSnapshot(quarter=2, game_clock=400.0),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=50, away_score=48,
                home_score_after=52, away_score_after=48,
            ),
            momentum=MomentumSnapshot(),
            shot=ShotResult(made=True, points=2),
        )
        defaults.update(kwargs)
        return PossessionResult(**defaults)

    def test_high_intensity_gets_full(self):
        p = self._make_possession()
        level = self.scorer.score(p, 0.8)
        assert level == VerbosityLevel.FULL

    def test_low_intensity_gets_condensed_or_skipped(self):
        p = self._make_possession()
        level = self.scorer.score(p, 0.2)
        assert level in (VerbosityLevel.CONDENSED, VerbosityLevel.SKIPPED)

    def test_blowout_q4_gets_skipped(self):
        p = self._make_possession(
            clock=ClockSnapshot(quarter=4, game_clock=300.0),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=120, away_score=90,
                home_score_after=122, away_score_after=90,
            ),
        )
        level = self.scorer.score(p, 0.1)
        assert level == VerbosityLevel.SKIPPED

    def test_lead_change_gets_full(self):
        p = self._make_possession(
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=48, away_score=50,
                home_score_after=51, away_score_after=50,
            ),
        )
        level = self.scorer.score(p, 0.4)
        assert level == VerbosityLevel.FULL

    def test_dunk_gets_full(self):
        p = self._make_possession(
            shot=ShotResult(made=True, points=2, is_dunk=True),
        )
        level = self.scorer.score(p, 0.4)
        assert level == VerbosityLevel.FULL

    def test_no_more_than_3_consecutive_skips(self):
        """After 3 skips, the next should be bumped to condensed."""
        levels = []
        for _ in range(5):
            p = self._make_possession(
                clock=ClockSnapshot(quarter=4, game_clock=300.0),
                score=ScoreSnapshot(
                    home_team="C", away_team="K",
                    home_score=120, away_score=90,
                    home_score_after=122, away_score_after=90,
                ),
            )
            level = self.scorer.score(p, 0.05)
            levels.append(level)

        # Should not have more than 3 consecutive skips
        max_consecutive = 0
        current_run = 0
        for lv in levels:
            if lv == VerbosityLevel.SKIPPED:
                current_run += 1
                max_consecutive = max(max_consecutive, current_run)
            else:
                current_run = 0
        assert max_consecutive <= 3
