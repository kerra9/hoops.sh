"""Short clause-style fragment templates for chain composition.

These fragments are used inside the ChainComposer to weave consecutive
actions into flowing prose. Unlike full-sentence templates, fragments
omit the subject (no repeated player name) and end with commas,
ellipses, or dashes instead of periods.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Dribble fragments (no period, no subject repetition)
# ---------------------------------------------------------------------------

DRIBBLE_FRAGMENTS = {
    "crossover": [
        "crosses over",
        "hits the crossover",
        "snaps it to the left",
        "crosses over, gets a step",
        "quick cross",
        "cross left",
    ],
    "hesitation": [
        "hits the hesi",
        "hesitation",
        "little hesi",
        "freezes the defender with the hesi",
        "stop-and-go",
        "gives a little stutter",
    ],
    "spin_move": [
        "spins",
        "spin move",
        "spins off the defender",
        "whirls into the lane",
        "reverse pivot",
    ],
    "step_back": [
        "step-back",
        "creates space with the step-back",
        "rocks back",
        "pulls back",
        "step-back for the jumper",
    ],
    "behind_the_back": [
        "goes behind the back",
        "behind the back",
        "wraps it around",
        "behind-the-back shift",
    ],
    "in_and_out": [
        "in-and-out",
        "fakes the cross with the in-and-out",
        "in-and-out, the defender bites",
        "sells the in-and-out",
    ],
    "between_the_legs": [
        "between the legs",
        "through the legs",
        "between-the-legs shift",
    ],
    "snatch_back": [
        "snatch-back",
        "pulls it back",
        "quick snatch-back",
    ],
    "shamgod": [
        "SHAMGOD",
        "pulls out the Shamgod",
        "the Shamgod!",
    ],
    "harden_step_back": [
        "the Harden step-back",
        "step-back from deep",
        "that patented step-back",
    ],
}

# Fallback fragments for unknown dribble types
DRIBBLE_FRAGMENTS_GENERIC = [
    "makes a move",
    "works the handle",
    "probes the defense",
    "changes direction",
    "shifts gears",
]

# ---------------------------------------------------------------------------
# Drive fragments
# ---------------------------------------------------------------------------

DRIVE_FRAGMENTS = [
    "attacks left",
    "attacks right",
    "drives baseline",
    "gets into the paint",
    "turns the corner",
    "goes downhill",
    "puts his head down and drives",
    "takes it strong",
    "explodes to the rim",
    "slashes into the lane",
    "penetrates into the key",
    "gets a step and goes",
    "blows by the defender",
    "attacks off the bounce",
    "takes it to the hole",
]

DRIVE_DIRECTION_FRAGMENTS = {
    "left": ["attacks left", "drives left", "goes left"],
    "right": ["attacks right", "drives right", "goes right"],
    "baseline": ["drives baseline", "goes baseline", "takes it baseline"],
    "middle": ["takes it middle", "goes up the gut", "drives middle"],
}

# ---------------------------------------------------------------------------
# Connector fragments (between action clusters)
# ---------------------------------------------------------------------------

SEPARATION_CONNECTORS = [
    "gets a step...",
    "creates space...",
    "has room now...",
    "the defender reaches...",
    "the defender is on his heels...",
    "a sliver of daylight...",
]

TRANSITION_CONNECTORS = [
    "then",
    "now",
    "and",
]

# ---------------------------------------------------------------------------
# Shot resolution fragments
# ---------------------------------------------------------------------------

SHOT_SETUP_FRAGMENTS = [
    "pulls up...",
    "fires...",
    "lets it fly...",
    "rises up...",
    "elevates...",
    "shoots over the defender...",
    "catches and fires...",
    "gathers and shoots...",
    "squares up...",
    "loads up...",
]

# ---------------------------------------------------------------------------
# Screen fragments
# ---------------------------------------------------------------------------

SCREEN_SETUP_FRAGMENTS = [
    "calls for the screen",
    "uses the pick",
    "comes off the screen",
    "waits for the screen",
]

SCREEN_RESULT_FRAGMENTS = [
    "defender goes under",
    "defender fights over",
    "they switch it",
    "hard hedge, pulls it back out",
]

# ---------------------------------------------------------------------------
# Pass fragments
# ---------------------------------------------------------------------------

PASS_FRAGMENTS = [
    "swings it to {receiver}",
    "finds {receiver}",
    "kicks to {receiver}",
    "dishes to {receiver}",
    "hits {receiver}",
    "gets it to {receiver}",
    "moves it to {receiver}",
    "extra pass to {receiver}",
    "skip pass to {receiver}",
]

# ---------------------------------------------------------------------------
# Catch-and-shoot fragments
# ---------------------------------------------------------------------------

CATCH_AND_SHOOT_FRAGMENTS = [
    "catches and fires",
    "catches, shoots",
    "catch-and-release",
    "in rhythm",
    "lets it go",
    "rises and fires",
]

# ---------------------------------------------------------------------------
# Probing / sizing-up fragments
# ---------------------------------------------------------------------------

PROBING_FRAGMENTS = [
    "surveys the defense",
    "sizes up the defender",
    "surveys the floor",
    "looking for an opening",
    "working the clock",
    "no rush",
    "patient with the ball",
    "probing the defense",
    "feeling out the defense",
    "waiting for something to develop",
]
