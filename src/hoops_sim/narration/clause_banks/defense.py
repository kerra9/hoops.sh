"""Clause bank for defender dignity descriptions and defensive actions."""

from hoops_sim.narration.clause_banks import ClauseBank

# Defender dignity-to-language mapping
DEFENDER_DIGNITY: ClauseBank = {
    "defender_status": {
        "composed": [  # dignity 0.8-1.0
            "{defender} stays in front",
            "good defense by {defender}",
            "{defender} matches step for step",
            "{defender} contests well",
            "{defender} holds his ground",
            "solid defense from {defender}",
            "{defender} stays with him",
            "{defender} doesn't give an inch",
        ],
        "reaching": [  # dignity 0.6-0.8
            "{defender} reaching",
            "{defender} a step behind",
            "{defender} trying to recover",
            "{defender} giving ground",
            "{defender} has to reach",
            "{defender} losing position",
            "{defender} scrambling to stay close",
            "{defender} getting beat off the dribble",
        ],
        "struggling": [  # dignity 0.4-0.6
            "{defender} struggling to keep up",
            "{defender} can't stay in front",
            "{defender} has lost a step",
            "{defender} can't keep up",
            "{defender} getting cooked",
            "{defender} on his heels",
            "{defender} in trouble",
            "{defender} getting torched",
        ],
        "stumbling": [  # dignity 0.2-0.4
            "{defender} stumbles!",
            "{defender} is lost!",
            "{defender} got caught!",
            "{defender} is reeling!",
            "{defender} can't recover!",
            "{defender} is beat badly!",
            "look at {defender}... completely lost!",
            "{defender} has been left behind!",
        ],
        "destroyed": [  # dignity 0.0-0.2
            "{DEFENDER} KISSES THE GROUND!",
            "{DEFENDER} IS ON THE FLOOR!",
            "{DEFENDER} IS DONE!",
            "{DEFENDER} HAS BEEN DESTROYED!",
            "LOOK AT {DEFENDER}! ON SKATES!",
            "{DEFENDER} SENT TO THE SHADOW REALM!",
            "{DEFENDER} FELL DOWN! OH MY!",
            "{DEFENDER} IS ON THE GROUND! SOMEBODY CALL AN AMBULANCE!",
        ],
    },
}

BLOCK_CLAUSES: ClauseBank = {
    "block": {
        "calm": [
            "blocked by {blocker}",
            "{blocker} with the block",
            "{blocker} gets a hand on it",
            "rejected by {blocker}",
        ],
        "building": [
            "{blocker} blocks the shot!",
            "REJECTED by {blocker}!",
            "{blocker} sends it away!",
            "{blocker} with the denial!",
        ],
        "hype": [
            "BLOCKED! {blocker} with the rejection!",
            "GET THAT OUTTA HERE! {blocker}!",
            "{blocker} SWATS it away!",
            "REJECTED! {blocker} says NO!",
        ],
        "screaming": [
            "BLOCKED! GET THAT OUTTA HERE!",
            "{BLOCKER} SENDS IT INTO THE STANDS!",
            "REJECTED! {BLOCKER} WITH THE MONSTER BLOCK!",
            "NOT IN MY HOUSE! {BLOCKER} SAYS NO!",
        ],
    },
}


def dignity_band(dignity: float) -> str:
    """Map defender dignity to a description band."""
    if dignity >= 0.8:
        return "composed"
    if dignity >= 0.6:
        return "reaching"
    if dignity >= 0.4:
        return "struggling"
    if dignity >= 0.2:
        return "stumbling"
    return "destroyed"


def get_defender_clauses(dignity: float) -> list[str]:
    """Get defender status clauses based on dignity level."""
    band = dignity_band(dignity)
    return DEFENDER_DIGNITY["defender_status"].get(
        band, DEFENDER_DIGNITY["defender_status"]["composed"],
    )


def get_block_clauses(band: str) -> list[str]:
    """Get block clauses at an intensity band."""
    return BLOCK_CLAUSES["block"].get(band, BLOCK_CLAUSES["block"]["calm"])
