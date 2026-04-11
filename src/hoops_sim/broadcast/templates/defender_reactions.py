"""Defender reaction templates for the broadcast layer.

30+ reactions organized by what the defender did in response to an offensive move.
Used by the ProseComposer to make defenders characters in the narration.
"""

from __future__ import annotations

# Defender got beaten by a move
BEATEN_REACTIONS: list[str] = [
    "bites hard",
    "lunges and misses",
    "over-commits",
    "goes for the fake",
    "gets caught reaching",
    "loses his footing",
    "can't recover",
    "gets turned around",
    "is a step behind",
    "gets blown by",
]

# Defender stayed disciplined
DISCIPLINED_REACTIONS: list[str] = [
    "stays disciplined",
    "doesn't budge",
    "stays home",
    "holds his ground",
    "reads it perfectly",
    "mirrors perfectly",
    "stays in front",
    "isn't fooled",
    "stays patient",
]

# Defender recovered after initial bite
RECOVERY_REACTIONS: list[str] = [
    "recovers nicely",
    "gets back in position",
    "scrambles back",
    "recovers at the last second",
    "closes out quickly",
    "makes up the ground",
]

# Defender went down (ankle breaker)
FALLEN_REACTIONS: list[str] = [
    "goes DOWN",
    "hits the deck",
    "falls to the floor",
    "crumbles",
    "is on the ground",
    "stumbles and falls",
    "gets his ankles broken",
    "slips and goes down",
]

# Help defender rotates
HELP_REACTIONS: list[str] = [
    "rotates over",
    "comes to help",
    "slides over from the weak side",
    "picks up the driver",
    "walls up at the rim",
    "steps into the lane",
]

# Closeout reactions
CLOSEOUT_REACTIONS: list[str] = [
    "closes out hard",
    "flies at the shooter",
    "gets a hand up",
    "contests well",
    "gets out there in time",
    "arrives late",
    "can't get there",
]


def get_defender_reaction(reaction_type: str) -> list[str]:
    """Get reaction templates by type."""
    mapping = {
        "bites": BEATEN_REACTIONS,
        "beaten": BEATEN_REACTIONS,
        "stays_home": DISCIPLINED_REACTIONS,
        "disciplined": DISCIPLINED_REACTIONS,
        "recovers": RECOVERY_REACTIONS,
        "falls": FALLEN_REACTIONS,
        "ankle_breaker": FALLEN_REACTIONS,
        "help": HELP_REACTIONS,
        "closeout": CLOSEOUT_REACTIONS,
    }
    return mapping.get(reaction_type, BEATEN_REACTIONS)
