"""Play-to-FSM state assignment engine.

Translates a PlayDefinition into coordinated FSM states for all 5
offensive players. Each play becomes a script of micro-actions that
unfold over real ticks.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.engine.action_fsm import (
    ActionStateMachine,
    BallHandlerState,
    MovementIntent,
    OffBallOffenseState,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.plays.playbook import PlayDefinition, PlayType, PlayerRole
from hoops_sim.utils.rng import SeededRNG


@dataclass
class PlayAssignment:
    """A player's role and initial action in a play."""

    player_id: int
    role: PlayerRole
    initial_state: BallHandlerState | OffBallOffenseState
    target_position: Vec2
    intent: MovementIntent = MovementIntent.JOG
    ticks: int = 10


@dataclass
class PlayExecution:
    """A play broken down into per-player FSM assignments."""

    play: PlayDefinition
    assignments: list[PlayAssignment] = field(default_factory=list)
    phase: int = 0  # Current phase of the play (0=initial, 1=main, 2=read)
    ticks_elapsed: int = 0
    is_freelance: bool = False  # Play broke down, now freelancing


def assign_play_roles(
    play: PlayDefinition,
    player_ids: list[int],
    player_positions: list[Vec2],
    basket_position: Vec2,
    attacking_right: bool,
    rng: SeededRNG,
) -> PlayExecution:
    """Assign play roles to players and create initial FSM states.

    Args:
        play: The play to execute.
        player_ids: IDs of the 5 offensive players (index 0 = PG typically).
        player_positions: Current positions of the 5 players.
        basket_position: The basket being attacked.
        attacking_right: Whether attacking the right basket.
        rng: Random number generator.

    Returns:
        PlayExecution with per-player assignments.
    """
    execution = PlayExecution(play=play)

    # Map roles to positions based on play type
    role_targets = _calculate_role_targets(play.play_type, basket_position, attacking_right, rng)

    for i, (pid, pos) in enumerate(zip(player_ids, player_positions)):
        role = play.roles[i] if i < len(play.roles) else PlayerRole.SPACER
        target = role_targets.get(role, pos)

        # Determine initial state based on role
        if role == PlayerRole.BALL_HANDLER:
            state = BallHandlerState.CALLING_PLAY
            intent = MovementIntent.JOG
            ticks = rng.randint(5, 10)
        elif role == PlayerRole.SCREENER:
            state = OffBallOffenseState.SETTING_SCREEN
            intent = MovementIntent.JOG
            ticks = rng.randint(10, 20)
        elif role == PlayerRole.SHOOTER:
            state = OffBallOffenseState.RELOCATING
            intent = MovementIntent.JOG
            ticks = rng.randint(8, 15)
        elif role == PlayerRole.CUTTER:
            state = OffBallOffenseState.STANDING
            intent = MovementIntent.STAND
            ticks = rng.randint(10, 20)
        elif role == PlayerRole.POST_PLAYER:
            state = OffBallOffenseState.STANDING
            intent = MovementIntent.JOG
            ticks = rng.randint(5, 10)
        else:  # SPACER
            state = OffBallOffenseState.SPOTTING_UP
            intent = MovementIntent.JOG
            ticks = rng.randint(10, 30)

        execution.assignments.append(PlayAssignment(
            player_id=pid,
            role=role,
            initial_state=state,
            target_position=target,
            intent=intent,
            ticks=ticks,
        ))

    return execution


def apply_play_to_fsms(
    execution: PlayExecution,
    fsms: dict[int, ActionStateMachine],
) -> None:
    """Apply play assignments to player FSMs.

    Args:
        execution: The play execution plan.
        fsms: Dictionary mapping player_id -> FSM.
    """
    for assignment in execution.assignments:
        fsm = fsms.get(assignment.player_id)
        if fsm is None:
            continue
        fsm.transition_to(
            new_state=assignment.initial_state,
            ticks=assignment.ticks,
            target=assignment.target_position,
            intent=assignment.intent,
        )


def _calculate_role_targets(
    play_type: PlayType,
    basket_pos: Vec2,
    attacking_right: bool,
    rng: SeededRNG,
) -> dict[PlayerRole, Vec2]:
    """Calculate target positions for each role in a play."""
    sign = 1.0 if attacking_right else -1.0

    # Base positions relative to basket
    if play_type == PlayType.PICK_AND_ROLL:
        return {
            PlayerRole.BALL_HANDLER: Vec2(
                basket_pos.x - sign * 20.0 + rng.gauss(0, 1),
                basket_pos.y + rng.gauss(0, 2),
            ),
            PlayerRole.SCREENER: Vec2(
                basket_pos.x - sign * 17.0,
                basket_pos.y + rng.gauss(0, 1),
            ),
            PlayerRole.SHOOTER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + (12.0 if rng.random() < 0.5 else -12.0),
            ),
            PlayerRole.SPACER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + (-12.0 if rng.random() < 0.5 else 12.0),
            ),
        }

    elif play_type == PlayType.ISOLATION:
        return {
            PlayerRole.BALL_HANDLER: Vec2(
                basket_pos.x - sign * 18.0,
                basket_pos.y + rng.choice([-8.0, 0.0, 8.0]),
            ),
            PlayerRole.SPACER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.gauss(0, 6),
            ),
        }

    elif play_type == PlayType.POST_UP:
        return {
            PlayerRole.BALL_HANDLER: Vec2(
                basket_pos.x - sign * 20.0,
                basket_pos.y + rng.gauss(0, 2),
            ),
            PlayerRole.POST_PLAYER: Vec2(
                basket_pos.x - sign * 8.0,
                basket_pos.y + rng.choice([-6.0, 6.0]),
            ),
            PlayerRole.SHOOTER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.gauss(0, 8),
            ),
            PlayerRole.SPACER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.gauss(0, 8),
            ),
        }

    elif play_type == PlayType.FAST_BREAK:
        return {
            PlayerRole.BALL_HANDLER: Vec2(
                basket_pos.x - sign * 30.0,
                basket_pos.y,
            ),
            PlayerRole.CUTTER: Vec2(
                basket_pos.x - sign * 15.0,
                basket_pos.y + rng.choice([-10.0, 10.0]),
            ),
            PlayerRole.SHOOTER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.choice([-15.0, 15.0]),
            ),
            PlayerRole.SPACER: Vec2(
                basket_pos.x - sign * 35.0,
                basket_pos.y,
            ),
        }

    else:  # MOTION, OFF_SCREEN, HANDOFF, CUT
        return {
            PlayerRole.BALL_HANDLER: Vec2(
                basket_pos.x - sign * 22.0,
                basket_pos.y + rng.gauss(0, 3),
            ),
            PlayerRole.SCREENER: Vec2(
                basket_pos.x - sign * 15.0,
                basket_pos.y + rng.gauss(0, 4),
            ),
            PlayerRole.SHOOTER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.choice([-12.0, 12.0]),
            ),
            PlayerRole.CUTTER: Vec2(
                basket_pos.x - sign * 10.0,
                basket_pos.y + rng.gauss(0, 6),
            ),
            PlayerRole.SPACER: Vec2(
                basket_pos.x - sign * 24.0,
                basket_pos.y + rng.gauss(0, 8),
            ),
        }
