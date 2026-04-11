"""Track recent action chains for rich, contextual narration.

Instead of isolated template fills, the action chain tracker remembers
the recent significant micro-actions and can weave them into the
narration for shots and other key events. Recognizes patterns like
dribble combos, screen-to-drive sequences, and drive-to-kick-out
chains to produce contextual prose instead of joined descriptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ActionChainEntry:
    """A single entry in the action chain."""

    action_type: str  # "dribble_move", "screen", "pass", "drive", "cut", "probing"
    player_name: str
    description: str
    detail: str = ""  # move_type, pass_type, screen_type, etc.
    ticks_ago: int = 0


class ActionChainTracker:
    """Tracks recent significant micro-actions for rich narration.

    The chain is cleared at the start of each possession and accumulates
    significant actions. When a shot is taken, the chain provides context
    via pattern recognition and contextual prose generation.
    """

    def __init__(self, max_entries: int = 10) -> None:
        self.entries: List[ActionChainEntry] = []
        self.max_entries = max_entries
        self._tick_counter = 0

    def clear(self) -> None:
        """Clear the chain at the start of a new possession."""
        self.entries = []
        self._tick_counter = 0

    def tick(self) -> None:
        """Advance the tick counter."""
        self._tick_counter += 1

    def add(
        self,
        action_type: str,
        player_name: str,
        description: str,
        detail: str = "",
    ) -> None:
        """Add a significant action to the chain."""
        entry = ActionChainEntry(
            action_type=action_type,
            player_name=player_name,
            description=description,
            detail=detail,
            ticks_ago=self._tick_counter,
        )
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def build_shot_context(self, shooter_name: str) -> str:
        """Build a narrative context string from the action chain.

        Recognizes patterns and produces contextual prose instead of
        simply joining descriptions with spaces.
        """
        if not self.entries:
            return ""

        # Detect patterns
        dribble_combo = self._detect_dribble_combo()
        had_screen = self.had_screen()
        had_drive = self.had_drive()
        chain_seconds = self._tick_counter * 0.1

        parts: List[str] = []

        # Pattern: dribble combo into shot
        if dribble_combo and len(dribble_combo) >= 2:
            moves = [e.detail or e.description for e in dribble_combo]
            if len(moves) >= 3:
                parts.append(f"after working for {chain_seconds:.0f} seconds...")
            if had_screen:
                screen_entry = self._find_entry("screen")
                if screen_entry:
                    parts.append(f"off the screen from {screen_entry.player_name}...")
            # Don't repeat individual dribble descriptions -- the chain
            # composer handles that. Just note the combo.
            parts.append("combo into the shot")
        elif had_screen and not had_drive:
            screen_entry = self._find_entry("screen")
            if screen_entry:
                parts.append(f"off the screen from {screen_entry.player_name}...")
        elif had_drive:
            parts.append("after the drive...")
        elif chain_seconds > 6:
            parts.append(f"after working for {chain_seconds:.0f} seconds...")
        else:
            # Fallback: join descriptions
            for entry in self.entries[-3:]:
                parts.append(entry.description)

        return " ".join(parts)

    def _detect_dribble_combo(self) -> List[ActionChainEntry]:
        """Find consecutive dribble moves in the chain."""
        combo: List[ActionChainEntry] = []
        for entry in self.entries:
            if entry.action_type == "dribble_move":
                combo.append(entry)
            else:
                if len(combo) >= 2:
                    return combo
                combo = []
        return combo if len(combo) >= 2 else []

    def _find_entry(self, action_type: str) -> Optional[ActionChainEntry]:
        """Find the most recent entry of a given type."""
        for entry in reversed(self.entries):
            if entry.action_type == action_type:
                return entry
        return None

    def had_screen(self) -> bool:
        """Whether a screen was part of the chain."""
        return any(e.action_type == "screen" for e in self.entries)

    def had_dribble_move(self) -> bool:
        """Whether a dribble move was part of the chain."""
        return any(e.action_type == "dribble_move" for e in self.entries)

    def had_pass(self) -> bool:
        """Whether a pass was part of the chain."""
        return any(e.action_type == "pass" for e in self.entries)

    def had_drive(self) -> bool:
        """Whether a drive was part of the chain."""
        return any(e.action_type == "drive" for e in self.entries)

    @property
    def dribble_combo_count(self) -> int:
        """Number of consecutive dribble moves at the end of the chain."""
        count = 0
        for entry in reversed(self.entries):
            if entry.action_type == "dribble_move":
                count += 1
            else:
                break
        return count

    @property
    def chain_descriptions(self) -> List[str]:
        """All entry descriptions as a list for event population."""
        return [e.description for e in self.entries]

    @property
    def last_action(self) -> ActionChainEntry | None:
        return self.entries[-1] if self.entries else None
