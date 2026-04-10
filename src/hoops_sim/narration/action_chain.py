"""Track recent action chains for rich, contextual narration.

Instead of isolated template fills, the action chain tracker remembers
the 3-5 most recent significant micro-actions and can weave them into
the narration for shots and other key events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ActionChainEntry:
    """A single entry in the action chain."""

    action_type: str  # "dribble_move", "screen", "pass", "drive", "cut"
    player_name: str
    description: str
    ticks_ago: int = 0


class ActionChainTracker:
    """Tracks recent significant micro-actions for rich narration.

    The chain is cleared at the start of each possession and accumulates
    significant actions. When a shot is taken, the chain provides context.
    """

    def __init__(self, max_entries: int = 5) -> None:
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

    def add(self, action_type: str, player_name: str, description: str) -> None:
        """Add a significant action to the chain."""
        entry = ActionChainEntry(
            action_type=action_type,
            player_name=player_name,
            description=description,
            ticks_ago=self._tick_counter,
        )
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def build_shot_context(self, shooter_name: str) -> str:
        """Build a narrative context string from the action chain.

        Returns a multi-sentence description of how the shot was created.
        """
        if not self.entries:
            return ""

        parts = []
        for entry in self.entries:
            parts.append(entry.description)

        return " ".join(parts)

    def had_screen(self) -> bool:
        """Whether a screen was part of the chain."""
        return any(e.action_type == "screen" for e in self.entries)

    def had_dribble_move(self) -> bool:
        """Whether a dribble move was part of the chain."""
        return any(e.action_type == "dribble_move" for e in self.entries)

    def had_pass(self) -> bool:
        """Whether a pass was part of the chain."""
        return any(e.action_type == "pass" for e in self.entries)

    @property
    def last_action(self) -> ActionChainEntry | None:
        return self.entries[-1] if self.entries else None
