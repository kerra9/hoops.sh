"""Cross-cutting: Character System.

Models every participant in a possession as a character with an arc,
not a slot fill. Tracks defender dignity, builds player-specific
vocabulary profiles, and assigns character roles per possession.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DefenderState:
    """Tracks a defender's dignity through a possession.

    Dignity degrades as the defender gets beaten by moves,
    screens, and drives. It maps to language intensity.
    """

    name: str = ""
    dignity: float = 1.0  # 1.0 = fresh, composed; 0.0 = on the floor
    recovery_attempts: int = 0
    was_screened: bool = False
    was_crossed: bool = False
    is_on_ground: bool = False

    def on_move_beaten(self, separation: float, ankle_breaker: bool) -> None:
        """Degrade dignity when beaten by a dribble move."""
        self.dignity -= 0.15 + (separation * 0.1)
        if ankle_breaker:
            self.dignity = max(0.0, self.dignity - 0.5)
            self.is_on_ground = True
            self.was_crossed = True
        self.dignity = max(0.0, self.dignity)

    def on_screen_caught(self) -> None:
        """Degrade dignity when caught on a screen."""
        self.was_screened = True
        self.dignity = max(0.0, self.dignity - 0.1)

    def on_recovery(self) -> None:
        """Slight dignity recovery on successful recovery."""
        self.recovery_attempts += 1
        self.dignity = min(1.0, self.dignity + 0.05)

    def on_drive_beaten(self) -> None:
        """Degrade dignity when beaten on a drive."""
        self.dignity = max(0.0, self.dignity - 0.15)


@dataclass
class PlayerVocabulary:
    """Words and phrases associated with a player's style.

    Built once from the player model and cached. Makes the same
    crossover by Kyrie Irving read differently than by LeBron James.
    """

    movement_verbs: list[str] = field(default_factory=lambda: [
        "drives", "attacks", "pushes",
    ])
    shot_descriptions: list[str] = field(default_factory=lambda: [
        "pulls up", "fires", "shoots",
    ])
    dribble_adjectives: list[str] = field(default_factory=lambda: [
        "quick", "smooth", "sharp",
    ])
    size_references: list[str] = field(default_factory=list)

    @classmethod
    def for_play_style(cls, play_style: str) -> PlayerVocabulary:
        """Build a vocabulary profile from a play style descriptor."""
        styles = {
            "explosive": PlayerVocabulary(
                movement_verbs=["explodes", "rockets", "bursts", "launches"],
                shot_descriptions=["rises up", "elevates", "fires"],
                dribble_adjectives=["explosive", "electric", "lightning-quick"],
            ),
            "crafty": PlayerVocabulary(
                movement_verbs=["glides", "slithers", "weaves", "navigates"],
                shot_descriptions=["floats one up", "crafts", "maneuvers"],
                dribble_adjectives=["silky", "smooth", "filthy", "disgusting"],
            ),
            "powerful": PlayerVocabulary(
                movement_verbs=["bullies", "muscles", "powers", "barrels"],
                shot_descriptions=["forces", "wills it in", "hammers"],
                dribble_adjectives=["strong", "powerful", "forceful"],
            ),
            "methodical": PlayerVocabulary(
                movement_verbs=["works", "operates", "positions", "maneuvers"],
                shot_descriptions=["surveys", "calculates", "picks his spot"],
                dribble_adjectives=["patient", "deliberate", "controlled"],
            ),
        }
        return styles.get(play_style, cls())


@dataclass
class CharacterCast:
    """The cast of characters for a single possession.

    Each possession has a protagonist (handler), antagonist (defender),
    and optional supporting characters.
    """

    handler: str = ""
    defender: str = ""
    screener: str = ""
    help_defender: str = ""
    shooter: str = ""  # catch-and-shoot player
    defender_state: DefenderState = field(default_factory=DefenderState)

    @classmethod
    def from_events(cls, events: list) -> CharacterCast:
        """Build a character cast from enriched events."""
        from hoops_sim.narration.types import EnrichedEvent

        cast = cls()
        for ev in events:
            if not isinstance(ev, EnrichedEvent):
                continue
            if ev.player_name and not cast.handler:
                cast.handler = ev.player_name
            if ev.defender_name and not cast.defender:
                cast.defender = ev.defender_name
                cast.defender_state = DefenderState(name=ev.defender_name)

        return cast
