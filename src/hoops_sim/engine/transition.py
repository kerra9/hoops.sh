"""Transition and fast break engine with micro-actions.

After a defensive rebound or steal, evaluates whether to push the pace
in transition. Simulates lane filling, passing decisions, and scoring
reads based on the numerical advantage.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


class TransitionAdvantage(enum.Enum):
    """Numerical advantage in transition."""

    ONE_ON_ZERO = "1v0"
    TWO_ON_ONE = "2v1"
    THREE_ON_TWO = "3v2"
    FOUR_ON_THREE = "4v3"
    FIVE_ON_FIVE = "5v5"  # No advantage, set up half-court


@dataclass
class TransitionEvaluation:
    """Result of evaluating a transition opportunity."""

    should_push: bool
    advantage: TransitionAdvantage
    ball_handler_id: int | None = None
    scoring_chance: float = 0.0  # Probability of an easy bucket


def evaluate_transition(
    rebounder_speed: int,
    rebounder_transition_tendency: float,
    offense_positions: list[tuple[int, Vec2, int]],
    defense_positions: list[tuple[int, Vec2, int]],
    basket_position: Vec2,
    is_steal: bool,
    rng: SeededRNG,
) -> TransitionEvaluation:
    """Evaluate whether to push in transition.

    Args:
        rebounder_speed: Speed attribute of the player who got the ball.
        rebounder_transition_tendency: Tendency to push pace (0-1).
        offense_positions: List of (id, position, speed) for new offensive players.
        defense_positions: List of (id, position, speed) for retreating defenders.
        basket_position: The basket being attacked.
        is_steal: Whether this was a steal (more likely to push).
        rng: Random number generator.

    Returns:
        TransitionEvaluation with the decision.
    """
    # Count players ahead of the ball
    ball_x = basket_position.x  # Approximate
    offense_ahead = sum(
        1 for _, pos, _ in offense_positions
        if abs(pos.x - basket_position.x) < 35.0
    )
    defense_back = sum(
        1 for _, pos, _ in defense_positions
        if abs(pos.x - basket_position.x) < 30.0
    )

    # Determine advantage
    if defense_back == 0 and offense_ahead >= 1:
        advantage = TransitionAdvantage.ONE_ON_ZERO
        scoring_chance = 0.90
    elif offense_ahead >= defense_back + 2:
        advantage = TransitionAdvantage.TWO_ON_ONE
        scoring_chance = 0.70
    elif offense_ahead >= defense_back + 1:
        advantage = TransitionAdvantage.THREE_ON_TWO
        scoring_chance = 0.55
    elif offense_ahead >= defense_back:
        advantage = TransitionAdvantage.FOUR_ON_THREE
        scoring_chance = 0.40
    else:
        advantage = TransitionAdvantage.FIVE_ON_FIVE
        scoring_chance = 0.15

    # Decision to push
    push_threshold = 0.3
    if is_steal:
        push_threshold = 0.15  # More likely to push after steals
    push_score = (
        rebounder_speed / 99.0 * 0.3
        + rebounder_transition_tendency * 0.3
        + scoring_chance * 0.4
    )

    should_push = push_score > push_threshold

    # Find the ball handler (fastest player with the ball or nearest to it)
    ball_handler_id = None
    if offense_positions:
        ball_handler_id = offense_positions[0][0]

    return TransitionEvaluation(
        should_push=should_push,
        advantage=advantage,
        ball_handler_id=ball_handler_id,
        scoring_chance=scoring_chance,
    )
