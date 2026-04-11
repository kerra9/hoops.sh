"""Intensity engine: scores every possession on a 0.0-1.0 scale.

The intensity score drives everything in the broadcast layer: word count,
capitalization, exclamation density, whether color commentary fires,
and whether the possession gets full/condensed/skipped treatment.

Factor weights:
  - Score margin: 25%
  - Clock situation: 25%
  - Play quality: 20%
  - Player significance: 15%
  - Narrative arc: 15%
"""

from __future__ import annotations

from hoops_sim.events.game_events import PossessionResult
from hoops_sim.utils.math import clamp


class IntensityEngine:
    """Scores possession intensity on 0.0-1.0 scale."""

    # Weight distribution
    W_MARGIN = 0.25
    W_CLOCK = 0.25
    W_PLAY = 0.20
    W_PLAYER = 0.15
    W_ARC = 0.15

    def __init__(self) -> None:
        self._consecutive_team_scores: dict[str, int] = {}
        self._player_points: dict[int, int] = {}

    def score(self, possession: PossessionResult) -> float:
        """Compute intensity for a possession result.

        Returns a float between 0.0 (routine) and 1.0 (electric).
        """
        margin_score = self._score_margin(possession)
        clock_score = self._score_clock(possession)
        play_score = self._score_play_quality(possession)
        player_score = self._score_player_significance(possession)
        arc_score = self._score_narrative_arc(possession)

        raw = (
            self.W_MARGIN * margin_score
            + self.W_CLOCK * clock_score
            + self.W_PLAY * play_score
            + self.W_PLAYER * player_score
            + self.W_ARC * arc_score
        )

        # Track state for future scoring
        self._update_tracking(possession)

        return clamp(raw, 0.0, 1.0)

    def _score_margin(self, p: PossessionResult) -> float:
        """Closer games are more intense."""
        margin = p.score.margin_before
        if margin <= 3:
            return 1.0
        if margin <= 6:
            return 0.8
        if margin <= 10:
            return 0.5
        if margin <= 15:
            return 0.3
        if margin <= 25:
            return 0.15
        return 0.05  # blowout

    def _score_clock(self, p: PossessionResult) -> float:
        """Late-game and end-of-quarter situations are more intense."""
        q = p.clock.quarter
        gc = p.clock.game_clock

        # Overtime is always high intensity
        if q > 4:
            return 0.9 + (0.1 if gc < 60 else 0.0)

        # 4th quarter with tight margin
        if q == 4:
            if gc <= 30:
                return 1.0  # final 30 seconds
            if gc <= 120:
                return 0.85  # under 2 minutes
            if gc <= 300:
                return 0.6  # under 5 minutes
            return 0.4

        # End of any quarter
        if gc <= 30:
            return 0.6
        if gc <= 120:
            return 0.3

        return 0.1

    def _score_play_quality(self, p: PossessionResult) -> float:
        """How exciting was the play itself?"""
        score = 0.0

        # Dunks are exciting
        if p.shot and p.shot.is_dunk:
            score += 0.5

        # And-one plays
        if p.shot and p.shot.is_and_one:
            score += 0.4

        # Ankle breaker
        if p.action_chain and p.action_chain.outcome == "ankle_breaker":
            score += 0.6

        # Blocks
        if p.shot and p.shot.shot_result_type == "blocked":
            score += 0.4

        # Threes are exciting when made
        if p.shot and p.shot.made and p.shot.points == 3:
            score += 0.3

        # Contested makes are exciting
        if p.shot and p.shot.made and p.shot.contest_level in (
            "contested", "heavily_contested"
        ):
            score += 0.3

        # Steals leading to transition
        if p.turnover and p.turnover.turnover_type == "steal":
            score += 0.3

        # Deep threes
        if p.shot and p.shot.distance > 27:
            score += 0.2

        return clamp(score, 0.0, 1.0)

    def _score_player_significance(self, p: PossessionResult) -> float:
        """Star players and milestone moments are more significant."""
        score = 0.0

        if p.ball_handler and p.ball_handler.id in self._player_points:
            pts = self._player_points[p.ball_handler.id]
            if pts >= 40:
                score += 0.8
            elif pts >= 30:
                score += 0.5
            elif pts >= 20:
                score += 0.3

        # Check for scoring milestones (about to hit 20/30/40/50)
        if p.shot and p.shot.made and p.shot.shooter:
            current = self._player_points.get(p.shot.shooter.id, 0)
            new_total = current + p.shot.points
            for milestone in [20, 30, 40, 50]:
                if current < milestone <= new_total:
                    score += 0.6
                    break

        return clamp(score, 0.0, 1.0)

    def _score_narrative_arc(self, p: PossessionResult) -> float:
        """Scoring runs and momentum shifts increase intensity."""
        score = 0.0

        if p.momentum.scoring_run >= 10:
            score += 0.7
        elif p.momentum.scoring_run >= 8:
            score += 0.5
        elif p.momentum.scoring_run >= 5:
            score += 0.3

        if p.momentum.is_momentum_shift:
            score += 0.4

        if p.score.lead_changed:
            score += 0.5

        if p.score.is_tie:
            score += 0.3

        return clamp(score, 0.0, 1.0)

    def _update_tracking(self, p: PossessionResult) -> None:
        """Update internal tracking state after scoring a possession."""
        if p.shot and p.shot.made and p.shot.shooter:
            pid = p.shot.shooter.id
            self._player_points[pid] = (
                self._player_points.get(pid, 0) + p.shot.points
            )
        if p.foul and p.foul.free_throws_made > 0 and p.ball_handler:
            pid = p.ball_handler.id
            self._player_points[pid] = (
                self._player_points.get(pid, 0) + p.foul.free_throws_made
            )

    def get_player_points(self, player_id: int) -> int:
        """Get tracked points for a player."""
        return self._player_points.get(player_id, 0)
