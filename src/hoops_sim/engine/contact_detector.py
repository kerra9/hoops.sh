"""Tick-level contact detection between players.

Every tick, checks for proximity-based contacts that could generate
fouls. Feeds ContactEvents to the referee crew for adjudication.
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.engine.action_fsm import BallHandlerState, DefenderState
from hoops_sim.physics.contact import ContactEvent, ContactSeverity
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


@dataclass
class ContactCheck:
    """A potential contact between two players."""

    offensive_player_id: int
    defensive_player_id: int
    distance: float
    offensive_action: str
    defensive_action: str


def detect_contacts(
    offense_states: list[tuple[int, Vec2, object]],
    defense_states: list[tuple[int, Vec2, object]],
    ball_handler_id: int | None,
    basket_position: Vec2,
    rng: SeededRNG,
) -> list[ContactEvent]:
    """Detect contacts between offensive and defensive players.

    Args:
        offense_states: List of (player_id, position, fsm) for offense.
        defense_states: List of (player_id, position, fsm) for defense.
        ball_handler_id: ID of the current ball handler.
        basket_position: Position of the basket.
        rng: Random number generator.

    Returns:
        List of ContactEvents that need adjudication.
    """
    contacts: list[ContactEvent] = []

    for off_id, off_pos, off_fsm in offense_states:
        for def_id, def_pos, def_fsm in defense_states:
            dist = off_pos.distance_to(def_pos)

            # Only check players within contact range (< 3 feet)
            if dist > 3.0:
                continue

            contact = _evaluate_contact(
                off_id, off_pos, off_fsm,
                def_id, def_pos, def_fsm,
                dist, ball_handler_id, basket_position, rng,
            )
            if contact is not None:
                contacts.append(contact)

    return contacts


def _evaluate_contact(
    off_id: int,
    off_pos: Vec2,
    off_fsm: object,
    def_id: int,
    def_pos: Vec2,
    def_fsm: object,
    distance: float,
    ball_handler_id: int | None,
    basket_position: Vec2,
    rng: SeededRNG,
) -> ContactEvent | None:
    """Evaluate whether a proximity generates a contact event."""
    from hoops_sim.engine.action_fsm import ActionStateMachine

    # Get FSM states
    off_state = None
    def_state = None
    if isinstance(off_fsm, ActionStateMachine):
        off_state = off_fsm.current_state
    if isinstance(def_fsm, ActionStateMachine):
        def_state = def_fsm.current_state

    # Determine contact severity based on actions
    severity = ContactSeverity.NONE
    is_shooting = False
    is_screen = False

    # Driving contact
    if off_state == BallHandlerState.DRIVING and distance < 2.0:
        severity = _roll_severity(0.3, 0.4, 0.2, 0.1, rng)
        is_shooting = True  # Driving to score

    # Finishing contact (at the rim)
    elif off_state == BallHandlerState.FINISHING and distance < 2.5:
        severity = _roll_severity(0.2, 0.3, 0.3, 0.15, rng)
        is_shooting = True

    # Shooting contact (jump shot)
    elif off_state == BallHandlerState.PULLING_UP and distance < 2.0:
        # Check if defender is contesting
        if def_state == DefenderState.CONTESTING_SHOT:
            severity = _roll_severity(0.4, 0.3, 0.2, 0.08, rng)
        else:
            severity = _roll_severity(0.6, 0.25, 0.1, 0.03, rng)
        is_shooting = True

    # Post-up contact
    elif off_state == BallHandlerState.POSTING_UP and distance < 1.5:
        severity = _roll_severity(0.3, 0.4, 0.2, 0.08, rng)

    # Screen contact
    elif off_state in (None,) and distance < 1.5:
        # Could be a screen -- low severity usually
        severity = _roll_severity(0.5, 0.3, 0.15, 0.04, rng)
        is_screen = True

    if severity == ContactSeverity.NONE:
        return None

    # Determine if the defender was in legal position
    dist_to_basket = def_pos.distance_to(basket_position)
    defensive_set = distance > 1.0  # Had position established
    defensive_legal = dist_to_basket > 4.0 or defensive_set  # Outside restricted area

    return ContactEvent(
        severity=severity,
        offensive_player_id=off_id,
        defensive_player_id=def_id,
        position=off_pos,
        is_shooting=is_shooting,
        defensive_set=defensive_set,
        defensive_legal_position=defensive_legal,
    )


def _roll_severity(
    none_weight: float,
    light_weight: float,
    moderate_weight: float,
    hard_weight: float,
    rng: SeededRNG,
) -> ContactSeverity:
    """Roll for contact severity from weighted probabilities."""
    roll = rng.random()
    if roll < none_weight:
        return ContactSeverity.NONE
    elif roll < none_weight + light_weight:
        return ContactSeverity.LIGHT
    elif roll < none_weight + light_weight + moderate_weight:
        return ContactSeverity.MODERATE
    elif roll < none_weight + light_weight + moderate_weight + hard_weight:
        return ContactSeverity.HARD
    else:
        return ContactSeverity.FLAGRANT
