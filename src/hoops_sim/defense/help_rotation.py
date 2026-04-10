"""Help defense and rotation chain logic.

When the ball handler beats their defender, a help defender must rotate
to stop the drive. This creates a 4-on-3 advantage for the offense.
The defense then rotates to cover the open player, creating a chain
of rotations. If the offense moves the ball faster than the defense
rotates, someone ends up open.
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2


@dataclass
class HelpRotationResult:
    """Result of a help defense rotation evaluation."""

    help_defender_id: int | None = None
    open_player_id: int | None = None  # Who the rotation leaves open
    rotation_quality: float = 0.5  # 0-1, how well the defense rotated
    drive_stopped: bool = False
    kick_out_available: bool = False


def evaluate_help_rotation(
    ball_handler_pos: Vec2,
    ball_handler_defender_pos: Vec2,
    basket_pos: Vec2,
    other_defenders: list[tuple[int, Vec2, Vec2, int]],
    offense_positions: list[tuple[int, Vec2]],
) -> HelpRotationResult:
    """Evaluate whether help defense is needed and who rotates.

    Args:
        ball_handler_pos: Ball handler's position.
        ball_handler_defender_pos: On-ball defender's position.
        basket_pos: Basket position.
        other_defenders: List of (player_id, position, assignment_pos, iq).
        offense_positions: List of (player_id, position) for non-handler offense.

    Returns:
        HelpRotationResult describing the help situation.
    """
    # Check if the on-ball defender has been beaten
    handler_to_basket = basket_pos.distance_to(ball_handler_pos)
    defender_to_basket = basket_pos.distance_to(ball_handler_defender_pos)
    separation = ball_handler_pos.distance_to(ball_handler_defender_pos)

    # Defender is beaten if handler is closer to basket and has separation
    beaten = (handler_to_basket < defender_to_basket - 2.0 and separation > 4.0)

    if not beaten:
        return HelpRotationResult(drive_stopped=True, rotation_quality=1.0)

    # Find the best help defender: closest to the driving lane
    # who isn't guarding someone in a dangerous position
    best_helper = None
    best_helper_score = -1.0

    for def_id, def_pos, assign_pos, iq in other_defenders:
        dist_to_handler = def_pos.distance_to(ball_handler_pos)
        dist_to_basket = def_pos.distance_to(basket_pos)

        # Prefer defenders who are:
        # 1. Close to the driving lane
        # 2. Close to the basket (interior defenders)
        # 3. High IQ (better help defenders)
        score = (
            (1.0 - dist_to_handler / 30.0) * 0.4
            + (1.0 - dist_to_basket / 30.0) * 0.3
            + iq / 99.0 * 0.3
        )

        if score > best_helper_score:
            best_helper_score = score
            best_helper = (def_id, def_pos, assign_pos)

    if best_helper is None:
        return HelpRotationResult(drive_stopped=False)

    helper_id, helper_pos, helper_assign_pos = best_helper

    # The helper's assignment is now open -- find who that is
    open_player_id = None
    for off_id, off_pos in offense_positions:
        if off_pos.distance_to(helper_assign_pos) < 8.0:
            open_player_id = off_id
            break

    # Rotation quality depends on how fast/smart the remaining defenders react
    avg_iq = sum(iq for _, _, _, iq in other_defenders) / max(1, len(other_defenders))
    rotation_quality = avg_iq / 99.0 * 0.7 + 0.3

    # Kick-out is available if there's an open perimeter player
    kick_out_available = False
    if open_player_id is not None:
        for off_id, off_pos in offense_positions:
            if off_id == open_player_id:
                dist_to_basket = off_pos.distance_to(basket_pos)
                if dist_to_basket > 20.0:  # Perimeter distance
                    kick_out_available = True
                break

    return HelpRotationResult(
        help_defender_id=helper_id,
        open_player_id=open_player_id,
        rotation_quality=rotation_quality,
        drive_stopped=True,
        kick_out_available=kick_out_available,
    )
