"""Tests for the IntensityEngine."""

from hoops_sim.broadcast.composer.intensity import IntensityEngine
from hoops_sim.events.game_events import (
    ClockSnapshot,
    MomentumSnapshot,
    PossessionResult,
    ScoreSnapshot,
    ShotResult,
    PlayerRef,
    TurnoverResult,
)


class TestIntensityEngine:
    def setup_method(self):
        self.engine = IntensityEngine()

    def _make_possession(self, **kwargs):
        defaults = dict(
            clock=ClockSnapshot(quarter=2, game_clock=400.0),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=50, away_score=48,
                home_score_after=50, away_score_after=48,
            ),
            momentum=MomentumSnapshot(),
            shot=ShotResult(made=True, points=2),
        )
        defaults.update(kwargs)
        return PossessionResult(**defaults)

    def test_routine_play_low_intensity(self):
        """Routine play in a blowout early in the game should be low intensity."""
        p = self._make_possession(
            clock=ClockSnapshot(quarter=2, game_clock=500.0),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=60, away_score=35,
                home_score_after=62, away_score_after=35,
            ),
        )
        intensity = self.engine.score(p)
        assert intensity < 0.4

    def test_clutch_moment_high_intensity(self):
        """Close game in Q4 under 2 minutes should be high intensity."""
        p = self._make_possession(
            clock=ClockSnapshot(quarter=4, game_clock=90.0, is_clutch=True),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=105, away_score=104,
                home_score_after=108, away_score_after=104,
            ),
            shot=ShotResult(made=True, points=3),
        )
        intensity = self.engine.score(p)
        assert intensity > 0.5  # Q4 close game with made three

    def test_dunk_increases_play_quality(self):
        p = self._make_possession(
            shot=ShotResult(made=True, points=2, is_dunk=True),
        )
        p_no_dunk = self._make_possession(
            shot=ShotResult(made=True, points=2, is_dunk=False),
        )
        assert self.engine.score(p) > self.engine.score(p_no_dunk)

    def test_scoring_run_increases_intensity(self):
        p = self._make_possession(
            momentum=MomentumSnapshot(scoring_run=12, run_team="Celtics"),
        )
        p_no_run = self._make_possession(
            momentum=MomentumSnapshot(scoring_run=0),
        )
        engine1 = IntensityEngine()
        engine2 = IntensityEngine()
        assert engine1.score(p) > engine2.score(p_no_run)

    def test_intensity_bounded(self):
        """Intensity should always be 0.0-1.0."""
        for _ in range(20):
            p = self._make_possession()
            intensity = self.engine.score(p)
            assert 0.0 <= intensity <= 1.0

    def test_player_tracking(self):
        """Player points should be tracked across possessions."""
        shooter = PlayerRef(id=1, name="Marcus Williams", team="Celtics")
        for _ in range(5):
            p = self._make_possession(
                shot=ShotResult(shooter=shooter, made=True, points=3),
            )
            self.engine.score(p)
        assert self.engine.get_player_points(1) == 15
