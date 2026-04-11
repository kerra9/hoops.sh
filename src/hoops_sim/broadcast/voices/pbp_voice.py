"""Play-by-play announcer voice.

Present tense, punchy clauses. Calm-to-explosive based on intensity.
Handles the real-time narration of what's happening on the court.
"""

from __future__ import annotations

import random
from typing import Optional

from hoops_sim.events.game_events import PossessionResult, ShotResult


class PBPVoice:
    """Play-by-play announcer voice.

    Characteristics:
    - Present tense: "drives", "pulls up", "fires"
    - Punchy clauses connected by dashes and ellipses
    - Calm at low intensity, explosive at high intensity
    - Signature phrases: "BANG!", "GOT IT!", "FROM DOWNTOWN!"
    """

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()

    def call_made_three(self, shooter: str, intensity: float) -> str:
        """Call a made three-pointer."""
        if intensity >= 0.9:
            return self._pick([
                f"{shooter} for THREE... BANG! FROM WAY DOWNTOWN!",
                f"{shooter}... GOT IT! THE THREE IS GOOD! WHAT A SHOT!",
                f"DRAINS IT! {shooter} FROM DEEP! OH MY GOODNESS!",
                f"{shooter} pulls up... YES! BANG! THE THREE!",
                f"ARE YOU KIDDING ME?! {shooter} BURIES THE THREE!",
            ])
        if intensity >= 0.7:
            return self._pick([
                f"{shooter} knocks down the three!",
                f"{shooter} drills it from deep!",
                f"{shooter} for three... got it!",
                f"{shooter} buries the three-pointer!",
                f"The three is GOOD from {shooter}!",
            ])
        if intensity >= 0.4:
            return self._pick([
                f"{shooter} hits the three.",
                f"{shooter} from three. Good.",
                f"Three-pointer, {shooter}.",
                f"{shooter} connects from deep.",
            ])
        return f"{shooter} with the three."

    def call_made_two(self, shooter: str, shot: ShotResult, intensity: float) -> str:
        """Call a made two-pointer."""
        ft = shot.finish_type or shot.shot_type or "jumper"
        ft_clean = ft.replace("_", " ")

        if intensity >= 0.8:
            return self._pick([
                f"{shooter} with the {ft_clean}... GOT IT!",
                f"{shooter}, BEAUTIFUL {ft_clean}!",
                f"WHAT A MOVE! {shooter} scores on the {ft_clean}!",
            ])
        if intensity >= 0.5:
            return self._pick([
                f"{shooter} with the {ft_clean}!",
                f"{shooter} scores on the {ft_clean}.",
                f"{shooter} finishes with the {ft_clean}!",
            ])
        return f"{shooter} {ft_clean}. Good."

    def call_dunk(self, shooter: str, intensity: float) -> str:
        """Call a dunk."""
        if intensity >= 0.85:
            return self._pick([
                f"{shooter} THROWS IT DOWN! WHAT A SLAM!",
                f"POSTER! {shooter} WITH THE MONSTER JAM!",
                f"OH MY! {shooter} WITH THE THUNDEROUS DUNK!",
                f"{shooter} RISES UP AND HAMMERS IT HOME!",
                f"{shooter} WITH THE FACIAL! UNBELIEVABLE!",
            ])
        if intensity >= 0.5:
            return self._pick([
                f"{shooter} throws it down!",
                f"{shooter} with the slam!",
                f"{shooter} dunks it!",
            ])
        return f"{shooter} with the dunk."

    def call_miss(self, shooter: str, shot: ShotResult, intensity: float) -> str:
        """Call a missed shot."""
        if shot.shot_result_type == "airball":
            if intensity >= 0.4:
                return f"{shooter} shoots... AIRBALL!"
            return f"{shooter} airballs it."

        if intensity >= 0.6:
            return self._pick([
                f"No good! {shooter} can't connect.",
                f"{shooter} fires and misses!",
                f"Off the mark from {shooter}!",
                f"{shooter} with the miss.",
            ])
        return self._pick([
            f"{shooter} misses.",
            f"No good from {shooter}.",
            f"Miss by {shooter}.",
        ])

    def call_block(self, blocker: str, shooter: str, intensity: float) -> str:
        """Call a blocked shot."""
        if intensity >= 0.7:
            return self._pick([
                f"{shooter} goes up... BLOCKED by {blocker}!",
                f"DENIED! {blocker} swats it away!",
                f"GET THAT OUT OF HERE! {blocker} with the rejection!",
                f"{blocker} says NO! What a block!",
            ])
        return self._pick([
            f"Blocked by {blocker}.",
            f"{blocker} with the block.",
        ])

    def call_steal(self, stealer: str, intensity: float) -> str:
        """Call a steal."""
        if intensity >= 0.6:
            return self._pick([
                f"{stealer} STRIPS IT! Steal!",
                f"PICKED OFF by {stealer}!",
                f"{stealer} jumps the passing lane!",
                f"Ripped away by {stealer}!",
            ])
        return self._pick([
            f"Stolen by {stealer}.",
            f"{stealer} with the steal.",
        ])

    def _pick(self, templates: list[str]) -> str:
        return self._rng.choice(templates)
