"""Clause bank for reactions: crowd, staredown, celebration, announcer."""

from hoops_sim.narration.clause_banks import ClauseBank

ANNOUNCER_REACTIONS: ClauseBank = {
    "announcer": {
        "calm": [
            "nice play",
            "good basketball",
            "well executed",
            "solid play",
        ],
        "building": [
            "what a play",
            "beautiful basketball",
            "that was impressive",
            "you love to see that",
            "great execution there",
        ],
        "hype": [
            "WHAT A PLAY!",
            "MY GOODNESS!",
            "LOOK AT THIS!",
            "INCREDIBLE!",
            "UNBELIEVABLE!",
            "WHAT A MOVE!",
            "ARE YOU KIDDING ME!",
            "OH MY!",
        ],
        "screaming": [
            "MY GOODNESS, WHAT A PLAY!",
            "ARE YOU KIDDING ME?! UNBELIEVABLE!",
            "I CANNOT BELIEVE WHAT I JUST SAW!",
            "WHAT ON EARTH?! THAT WAS INCREDIBLE!",
            "OH! MY! GOODNESS!",
            "GIVE THAT MAN A STATUE!",
            "DID THAT JUST HAPPEN?! REPLAY THAT!",
            "SOMEBODY CALL THE AUTHORITIES! THAT'S CRIMINAL!",
        ],
    },
}

CROWD_REACTIONS: ClauseBank = {
    "crowd": {
        "calm": [
            "the crowd murmurs",
            "scattered applause",
            "polite appreciation from the crowd",
        ],
        "building": [
            "the crowd starting to buzz",
            "the energy is building",
            "the fans sense something happening",
            "the arena coming alive",
        ],
        "hype": [
            "the crowd is ON ITS FEET!",
            "listen to this building!",
            "the arena ERUPTS!",
            "deafening roar from the crowd!",
            "the place is going CRAZY!",
            "the fans are LOVING this!",
            "PANDEMONIUM!",
            "the crowd goes WILD!",
        ],
        "screaming": [
            "THE CROWD IS GOING ABSOLUTELY INSANE!",
            "LISTEN TO THIS PLACE! DEAFENING!",
            "THE ARENA IS SHAKING!",
            "THE FANS ARE LOSING THEIR MINDS!",
            "I CAN'T EVEN HEAR MYSELF THINK!",
            "THE BUILDING IS ABOUT TO EXPLODE!",
            "PANDEMONIUM IN THE ARENA!",
            "THIS CROWD IS ELECTRIC!",
        ],
    },
}

STAREDOWN: ClauseBank = {
    "staredown": {
        "calm": [
            "looks at the defender",
            "glances at {defender}",
        ],
        "building": [
            "gives {defender} a look",
            "stares at {defender}",
            "looks right at {defender}",
        ],
        "hype": [
            "STARES {defender} DOWN!",
            "gives {defender} THE LOOK!",
            "looks right at {defender}! Cold-blooded!",
            "stares down {defender}! Ice in his veins!",
        ],
        "screaming": [
            "STARES HIM DOWN! COLD AS ICE!",
            "LOOKS RIGHT AT {DEFENDER}! THE DISRESPECT!",
            "THE STAREDOWN! ICE IN HIS VEINS!",
            "STARES {DEFENDER} DOWN! ABSOLUTELY RUTHLESS!",
        ],
    },
}

SEPARATION: ClauseBank = {
    "separation": {
        "calm": [
            "gets a step",
            "creates a little space",
        ],
        "building": [
            "gets a step of separation",
            "creates some daylight",
            "has a step on {defender}",
        ],
        "hype": [
            "LOOK AT THIS SEPARATION!",
            "wide open! All alone!",
            "created SO MUCH SPACE!",
            "all the room in the world!",
        ],
        "screaming": [
            "LOOK AT THIS SEPARATION! ACRES OF SPACE!",
            "ALL ALONE! WIDE OPEN! NOBODY WITHIN 5 FEET!",
            "THE SEPARATION IS ABSURD!",
            "CREATED SO MUCH SPACE {DEFENDER} NEEDS A GPS!",
        ],
    },
}


def get_announcer_reactions(band: str) -> list[str]:
    """Get announcer reaction clauses at an intensity band."""
    return ANNOUNCER_REACTIONS["announcer"].get(
        band, ANNOUNCER_REACTIONS["announcer"]["calm"],
    )


def get_crowd_reactions(band: str) -> list[str]:
    """Get crowd reaction clauses at an intensity band."""
    return CROWD_REACTIONS["crowd"].get(
        band, CROWD_REACTIONS["crowd"]["calm"],
    )


def get_staredown_clauses(band: str) -> list[str]:
    """Get staredown clauses at an intensity band."""
    return STAREDOWN["staredown"].get(
        band, STAREDOWN["staredown"]["calm"],
    )


def get_separation_clauses(band: str) -> list[str]:
    """Get separation clauses at an intensity band."""
    return SEPARATION["separation"].get(
        band, SEPARATION["separation"]["calm"],
    )
