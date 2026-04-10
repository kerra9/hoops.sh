"""Per-tick defensive micro-action decisions.

Each defender evaluates their situation every tick and decides what to do:
guard on-ball, deny a pass, help on a drive, close out on a shooter,
contest a shot, or box out for a rebound.
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.engine.action_fsm import (
    ActionStateMachine,
    DefenderState,
    MovementIntent,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


@dataclass
class DefensiveContext:
    """Information a defender needs to make a decision."""

    # Own attributes
    lateral_quickness: int
    perimeter_defense: int
    interior_defense: int
    steal_rating: int
    block_rating: int
    defensive_consistency: int
    basketball_iq: int

    # Tendencies
    gamble_for_steal: float
    help_tendency: float

    # Situation
    own_position: Vec2
    assignment_position: Vec2
    ball_position: Vec2
    ball_handler_position: Vec2
    basket_position: Vec2
    assignment_has_ball: bool
    ball_handler_driving: bool
    ball_handler_shooting: bool
    shot_in_air: bool
    assignment_distance: float
    ball_handler_distance: float
    help_needed: bool  # Ball handler beat their defender


def decide_defensive_action(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
    rng: SeededRNG,
) -> None:
    """Decide the next defensive micro-action for a player.

    Mutates the FSM in place with the chosen action.

    Args:
        ctx: Defensive context with all relevant information.
        fsm: The player's action state machine.
        rng: Random number generator.
    """
    # If shot is in the air, box out
    if ctx.shot_in_air:
        _decide_box_out(ctx, fsm)
        return

    # If assignment has the ball, guard on-ball
    if ctx.assignment_has_ball:
        _decide_on_ball_defense(ctx, fsm, rng)
        return

    # If ball handler is shooting, try to contest
    if ctx.ball_handler_shooting and ctx.ball_handler_distance < 8.0:
        _decide_contest(ctx, fsm)
        return

    # If ball handler is driving and help is needed
    if ctx.ball_handler_driving and ctx.help_needed:
        _decide_help_or_stay(ctx, fsm, rng)
        return

    # Default: deny pass to assignment
    _decide_off_ball_defense(ctx, fsm, rng)


def _decide_on_ball_defense(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
    rng: SeededRNG,
) -> None:
    """Decide on-ball defensive action."""
    # Stay in front of the ball handler
    # Position between assignment and basket
    to_basket = (ctx.basket_position - ctx.assignment_position).normalized()
    guard_pos = ctx.assignment_position + to_basket * 3.0

    # Gamble for steal?
    if (ctx.gamble_for_steal > 0.5
            and ctx.assignment_distance < 3.0
            and rng.random() < ctx.gamble_for_steal * 0.05):
        # Reach in -- risky but could get a steal
        fsm.transition_to(
            DefenderState.GUARDING_ON_BALL,
            ticks=5,
            target=ctx.assignment_position,
            intent=MovementIntent.LATERAL,
            context={"gambling": True},
        )
    else:
        fsm.transition_to(
            DefenderState.GUARDING_ON_BALL,
            ticks=5,
            target=guard_pos,
            intent=MovementIntent.LATERAL,
        )


def _decide_contest(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
) -> None:
    """Contest a shot attempt."""
    fsm.transition_to(
        DefenderState.CONTESTING_SHOT,
        ticks=4,
        target=ctx.ball_handler_position,
        intent=MovementIntent.SPRINT,
    )


def _decide_help_or_stay(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
    rng: SeededRNG,
) -> None:
    """Decide whether to help on a drive or stay home."""
    # Calculate help value: closer to basket + higher help tendency = more likely
    dist_to_ball_handler = ctx.ball_handler_distance
    dist_assignment_to_basket = ctx.assignment_position.distance_to(ctx.basket_position)

    help_value = (
        ctx.help_tendency * 0.3
        + ctx.interior_defense / 99.0 * 0.2
        + (1.0 - dist_to_ball_handler / 20.0) * 0.3
        + (1.0 - dist_assignment_to_basket / 30.0) * 0.2
    )

    if help_value > 0.5 or dist_to_ball_handler < 8.0:
        # Help on the drive: rotate toward the ball handler's driving path
        help_pos = _calculate_help_position(ctx)
        fsm.transition_to(
            DefenderState.HELPING,
            ticks=rng.randint(5, 10),
            target=help_pos,
            intent=MovementIntent.SPRINT,
            context={"helping_on": "drive"},
        )
    else:
        # Stay on assignment
        _decide_off_ball_defense(ctx, fsm, rng)


def _decide_off_ball_defense(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
    rng: SeededRNG,
) -> None:
    """Default off-ball defensive positioning."""
    # Position between assignment and basket, shading toward ball
    to_basket = (ctx.basket_position - ctx.assignment_position).normalized()
    to_ball = (ctx.ball_position - ctx.assignment_position).normalized()

    # Weight: 70% toward basket, 30% toward ball
    deny_offset = to_basket * 3.0 + to_ball * 1.5
    deny_pos = ctx.assignment_position + deny_offset

    fsm.transition_to(
        DefenderState.DENYING_PASS,
        ticks=rng.randint(5, 15),
        target=deny_pos,
        intent=MovementIntent.JOG,
    )


def _decide_box_out(
    ctx: DefensiveContext,
    fsm: ActionStateMachine,
) -> None:
    """Position for a rebound."""
    # Get between assignment and basket
    to_basket = (ctx.basket_position - ctx.assignment_position).normalized()
    box_out_pos = ctx.assignment_position + to_basket * 2.0

    fsm.transition_to(
        DefenderState.BOXING_OUT,
        ticks=8,
        target=box_out_pos,
        intent=MovementIntent.JOG,
    )


def _calculate_help_position(ctx: DefensiveContext) -> Vec2:
    """Calculate where a help defender should rotate to."""
    # Help position is between the ball handler and the basket,
    # but offset to cut off the driving lane
    handler_to_basket = (ctx.basket_position - ctx.ball_handler_position).normalized()
    help_point = ctx.ball_handler_position + handler_to_basket * 5.0
    return help_point


def calculate_closeout_quality(
    defender_position: Vec2,
    shooter_position: Vec2,
    defender_speed: int,
    closeout_ticks_elapsed: int,
) -> float:
    """Calculate how well a closeout is going.

    Returns a contest quality from 0 (wide open) to 1 (smothered).
    """
    distance = defender_position.distance_to(shooter_position)

    # Speed determines how fast the defender covers ground
    speed_factor = defender_speed / 99.0
    ground_covered = closeout_ticks_elapsed * speed_factor * 2.5  # ft per tick

    effective_distance = max(0.0, distance - ground_covered)

    # Convert to contest quality
    if effective_distance < 2.0:
        return 0.9  # Smothered
    elif effective_distance < 4.0:
        return 0.6  # Well contested
    elif effective_distance < 6.0:
        return 0.3  # Lightly contested
    else:
        return 0.05  # Wide open
