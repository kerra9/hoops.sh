"""Player tendencies: behavioral preferences that drive AI decisions.

Tendencies are separate from attributes. Attributes determine *ability*;
tendencies determine *preference*. A player with high three_point and high
shot_volume will shoot a lot of threes. A player with high three_point but
low shot_volume might be a great shooter who defers to teammates.

All tendency values are 0.0 to 1.0.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerTendencies:
    """20 tendency values that influence AI decision-making.

    All values range from 0.0 (never/minimal) to 1.0 (always/maximal).
    """

    # Offensive tendencies
    shot_volume: float = 0.5  # How often the player looks to shoot
    drive_tendency: float = 0.5  # Preference for driving to the rim
    three_point_tendency: float = 0.5  # Preference for shooting threes vs mid-range
    mid_range_tendency: float = 0.5  # Willingness to take mid-range shots
    post_up_tendency: float = 0.3  # Tendency to post up
    pass_first: float = 0.5  # Pass-first vs score-first mentality
    iso_tendency: float = 0.3  # Preference for isolation plays
    transition_tendency: float = 0.5  # Tendency to push in transition

    # Defensive tendencies
    gamble_for_steal: float = 0.3  # Willingness to reach/gamble on defense
    help_tendency: float = 0.5  # How quickly to help off their man
    closeout_aggression: float = 0.5  # How hard they close out on shooters
    foul_tendency: float = 0.3  # Likelihood of fouling (aggressive defense)

    # Effort tendencies
    crash_boards: float = 0.5  # Offensive rebounding effort
    hustle_plays: float = 0.5  # Diving for loose balls, contesting shots
    contest_shots: float = 0.6  # Effort to contest every shot

    # Behavioral tendencies
    emotional_volatility: float = 0.3  # How much emotions affect play
    complain_to_refs: float = 0.2  # Tendency to argue calls (tech risk)
    showboat: float = 0.2  # Tendency to showboat (momentum boost but risk)
    team_player: float = 0.7  # Willingness to sacrifice for the team
    clutch_desire: float = 0.5  # Wants the ball in clutch situations

    def validate(self) -> bool:
        """Check that all tendencies are in valid range."""
        for val in self.__dict__.values():
            if not isinstance(val, (int, float)):
                continue
            if val < 0.0 or val > 1.0:
                return False
        return True

    def clamp_all(self) -> None:
        """Clamp all tendency values to [0.0, 1.0]."""
        for key, val in self.__dict__.items():
            if isinstance(val, (int, float)):
                setattr(self, key, max(0.0, min(1.0, float(val))))
