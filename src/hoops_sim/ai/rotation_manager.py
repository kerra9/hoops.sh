"""Rotation intelligence for realistic substitution patterns.

Manages when players enter and exit the game based on NBA-realistic
rotation patterns: starters play 6-7 minutes to start, bench unit
comes in at the 5:00-7:00 mark, closers play the final 5 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RotationSlot:
    """A substitution opportunity."""

    player_out_id: int
    player_in_id: int
    urgency: float  # 0-1, how urgently this sub should happen
    reason: str


def evaluate_rotation(
    on_court_players: list[dict],
    bench_players: list[dict],
    quarter: int,
    game_clock: float,
    score_diff: int,
    is_close_game: bool,
) -> list[RotationSlot]:
    """Evaluate which substitutions should be made.

    Args:
        on_court_players: List of dicts with keys:
            id, overall, energy_pct, fouls, minutes_played, is_starter, position
        bench_players: List of dicts with same keys.
        quarter: Current quarter.
        game_clock: Seconds remaining in quarter.
        score_diff: Score difference from this team's perspective.
        is_close_game: Whether the game is within 10 points.

    Returns:
        List of RotationSlot recommendations, sorted by urgency.
    """
    slots: list[RotationSlot] = []
    minutes_in_quarter = (720.0 - game_clock) / 60.0

    for player in on_court_players:
        urgency = _calculate_sub_urgency(
            player, quarter, minutes_in_quarter, game_clock, score_diff, is_close_game,
        )
        if urgency > 0.4:
            # Find the best available replacement
            replacement = _find_best_replacement(player, bench_players)
            if replacement is not None:
                slots.append(RotationSlot(
                    player_out_id=player["id"],
                    player_in_id=replacement["id"],
                    urgency=urgency,
                    reason=_sub_reason(player, quarter, minutes_in_quarter),
                ))

    slots.sort(key=lambda s: s.urgency, reverse=True)
    return slots


def _calculate_sub_urgency(
    player: dict,
    quarter: int,
    minutes_in_quarter: float,
    game_clock: float,
    score_diff: int,
    is_close_game: bool,
) -> float:
    """Calculate how urgently a player needs to come out."""
    urgency = 0.0

    energy_pct = player["energy_pct"]
    fouls = player["fouls"]
    minutes = player["minutes_played"]
    is_starter = player["is_starter"]

    # Foul trouble
    if fouls >= 5:
        urgency += 0.8
    elif fouls >= 4 and quarter < 4:
        urgency += 0.5
    elif fouls >= 3 and quarter <= 2:
        urgency += 0.3

    # Energy-based
    if energy_pct < 0.25:
        urgency += 0.6
    elif energy_pct < 0.40:
        urgency += 0.35
    elif energy_pct < 0.55:
        urgency += 0.15

    # Minutes management
    if minutes > 38:
        urgency += 0.4
    elif minutes > 34:
        urgency += 0.2
    elif minutes > 28:
        urgency += 0.05

    # Rotation timing: starters come out at ~5-7 min mark
    if is_starter and 5.0 <= minutes_in_quarter <= 7.0 and quarter <= 2:
        if minutes > (minutes_in_quarter + (quarter - 1) * 12) * 0.9:
            urgency += 0.25

    # Closing time: keep best players in for close games
    if quarter >= 4 and game_clock < 300 and is_close_game:
        if is_starter:
            urgency *= 0.3  # Much less likely to sub starters in crunch time
        else:
            urgency += 0.3  # Bench players should come out for closers

    # Garbage time: sub out starters
    if quarter >= 4 and abs(score_diff) > 25:
        if is_starter and minutes > 20:
            urgency += 0.6

    return min(1.0, urgency)


def _find_best_replacement(player: dict, bench: list[dict]) -> dict | None:
    """Find the best available bench player to replace someone."""
    if not bench:
        return None

    # Prefer same position, highest overall, most rested
    candidates = []
    for b in bench:
        score = (
            b["overall"] / 99.0 * 0.4
            + b["energy_pct"] * 0.3
            + (1.0 if b.get("position") == player.get("position") else 0.5) * 0.3
        )
        candidates.append((b, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0] if candidates else None


def _sub_reason(player: dict, quarter: int, minutes_in_quarter: float) -> str:
    """Generate a human-readable reason for the substitution."""
    if player["fouls"] >= 5:
        return "foul trouble"
    if player["energy_pct"] < 0.30:
        return "fatigue"
    if player["minutes_played"] > 36:
        return "minutes management"
    if player["is_starter"] and 5.0 <= minutes_in_quarter <= 7.0:
        return "rotation"
    return "tactical"
