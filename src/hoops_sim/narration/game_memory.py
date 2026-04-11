"""Game memory and callback system for narrative continuity.

Tracks notable plays throughout the game so the broadcast can reference
earlier events: 'Same spot, same result!', 'Remember that blocked shot
in the second quarter? He just got his revenge.', etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from hoops_sim.utils.rng import SeededRNG


@dataclass
class MemorablePlay:
    """A notable play stored for potential callback references."""

    quarter: int
    game_clock: float
    play_type: str  # "block", "dunk", "ankle_breaker", "three", "steal", "miss"
    primary_player_id: int
    primary_player_name: str
    secondary_player_id: int = 0
    secondary_player_name: str = ""
    zone: str = ""
    description: str = ""


@dataclass
class Storyline:
    """A running storyline tracked across the game."""

    name: str  # e.g. "Mitchell vs Williams", "Hawks scoring run"
    description: str
    intensity: float = 0.5
    mentions: int = 0


class GameMemory:
    """Remembers notable plays and generates callback references.

    Stores blocks (for revenge drives), poster dunks, ankle breakers,
    clutch shots, big runs, and missed opportunities. When a related
    situation recurs, provides callback text for the analyst.
    """

    def __init__(self, rng: SeededRNG) -> None:
        self.rng = rng
        self._plays: List[MemorablePlay] = []
        self._storylines: List[Storyline] = []
        self._max_plays = 50
        self._max_storylines = 5
        # Track player zone history for "same spot" callbacks
        self._player_zone_history: Dict[int, List[Tuple[str, bool]]] = {}

    def record_block(
        self,
        quarter: int,
        game_clock: float,
        blocker_id: int,
        blocker_name: str,
        shooter_id: int,
        shooter_name: str,
    ) -> None:
        """Record a blocked shot for revenge-drive callbacks."""
        self._plays.append(MemorablePlay(
            quarter=quarter,
            game_clock=game_clock,
            play_type="block",
            primary_player_id=blocker_id,
            primary_player_name=blocker_name,
            secondary_player_id=shooter_id,
            secondary_player_name=shooter_name,
            description=(
                f"{blocker_name} blocked {shooter_name}"
            ),
        ))

    def record_shot(
        self,
        quarter: int,
        game_clock: float,
        shooter_id: int,
        shooter_name: str,
        zone: str,
        made: bool,
        is_clutch: bool = False,
        is_dunk: bool = False,
        defender_id: int = 0,
        defender_name: str = "",
    ) -> None:
        """Record a notable shot for location/matchup callbacks."""
        # Track zone history
        if shooter_id not in self._player_zone_history:
            self._player_zone_history[shooter_id] = []
        self._player_zone_history[shooter_id].append((zone, made))

        # Only store remarkable shots
        if is_clutch or is_dunk or not made:
            play_type = "dunk" if is_dunk else ("clutch_shot" if is_clutch else "miss")
            self._plays.append(MemorablePlay(
                quarter=quarter,
                game_clock=game_clock,
                play_type=play_type,
                primary_player_id=shooter_id,
                primary_player_name=shooter_name,
                secondary_player_id=defender_id,
                secondary_player_name=defender_name,
                zone=zone,
            ))

    def record_ankle_breaker(
        self,
        quarter: int,
        game_clock: float,
        handler_id: int,
        handler_name: str,
        defender_id: int,
        defender_name: str,
    ) -> None:
        """Record an ankle breaker for later callbacks."""
        self._plays.append(MemorablePlay(
            quarter=quarter,
            game_clock=game_clock,
            play_type="ankle_breaker",
            primary_player_id=handler_id,
            primary_player_name=handler_name,
            secondary_player_id=defender_id,
            secondary_player_name=defender_name,
        ))

    def record_steal(
        self,
        quarter: int,
        game_clock: float,
        stealer_id: int,
        stealer_name: str,
        victim_id: int,
        victim_name: str,
    ) -> None:
        """Record a steal."""
        self._plays.append(MemorablePlay(
            quarter=quarter,
            game_clock=game_clock,
            play_type="steal",
            primary_player_id=stealer_id,
            primary_player_name=stealer_name,
            secondary_player_id=victim_id,
            secondary_player_name=victim_name,
        ))

    def check_callback(
        self,
        event_type: str,
        player_id: int,
        player_name: str,
        zone: str = "",
        opponent_id: int = 0,
        opponent_name: str = "",
    ) -> Optional[str]:
        """Check if there's a callback reference for the current play.

        Returns callback text if a relevant earlier play exists, or None.
        """
        callbacks: List[str] = []

        for play in self._plays:
            # Revenge drive: player was blocked by opponent earlier
            if (
                event_type in ("drive", "shot_made", "dunk")
                and play.play_type == "block"
                and play.secondary_player_id == player_id
                and play.primary_player_id == opponent_id
            ):
                callbacks.append(
                    f"Remember that block by {play.primary_player_name} "
                    f"in the {_quarter_ordinal(play.quarter)}? "
                    f"{player_name} wants revenge!"
                )

            # Same spot callback
            if (
                event_type == "shot_made"
                and play.play_type == "miss"
                and play.primary_player_id == player_id
                and play.zone
                and play.zone.lower() == zone.lower()
            ):
                callbacks.append(
                    f"He missed from that exact spot earlier, "
                    f"but not this time!"
                )

            # Same spot success callback
            if (
                event_type == "shot_made"
                and play.play_type == "clutch_shot"
                and play.primary_player_id == player_id
                and play.zone
                and play.zone.lower() == zone.lower()
            ):
                callbacks.append(
                    "Same spot, same result! That's his office."
                )

        if not callbacks:
            return None

        return self.rng.choice(callbacks)

    def check_zone_callback(
        self,
        shooter_id: int,
        zone: str,
        made: bool,
    ) -> Optional[str]:
        """Check zone history for 'same spot' or 'favorite spot' callbacks."""
        history = self._player_zone_history.get(shooter_id, [])
        if len(history) < 2:
            return None

        # Count shots from this zone
        zone_shots = [(z, m) for z, m in history if z.lower() == zone.lower()]
        if len(zone_shots) >= 3:
            makes = sum(1 for _, m in zone_shots if m)
            if makes >= 2 and made:
                return "From his favorite spot on the floor."
            if not made and makes == 0:
                return "He keeps going back to that spot, but it's not falling."

        # Previous miss from same zone, now makes
        if made and len(zone_shots) >= 2:
            prev_made = zone_shots[-2][1]
            if not prev_made:
                return "He missed from there earlier, but not this time!"

        return None

    def add_storyline(self, name: str, description: str, intensity: float = 0.5) -> None:
        """Add or update a running storyline."""
        for sl in self._storylines:
            if sl.name == name:
                sl.description = description
                sl.intensity = intensity
                sl.mentions += 1
                return

        if len(self._storylines) >= self._max_storylines:
            # Remove least intense
            self._storylines.sort(key=lambda s: s.intensity)
            self._storylines.pop(0)

        self._storylines.append(Storyline(
            name=name,
            description=description,
            intensity=intensity,
        ))

    def get_active_storylines(self) -> List[Storyline]:
        """Return active storylines sorted by intensity."""
        active = [s for s in self._storylines if s.intensity > 0.2]
        active.sort(key=lambda s: s.intensity, reverse=True)
        return active[:3]

    @property
    def total_memorable_plays(self) -> int:
        return len(self._plays)


def _quarter_ordinal(quarter: int) -> str:
    """Convert quarter number to ordinal string."""
    names = {1: "1st quarter", 2: "2nd quarter", 3: "3rd quarter", 4: "4th quarter"}
    return names.get(quarter, f"OT{quarter - 4}")
