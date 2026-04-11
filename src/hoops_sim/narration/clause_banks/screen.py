"""Clause bank for screen action events."""

from hoops_sim.narration.clause_banks import ClauseBank

SCREEN_CLAUSES: ClauseBank = {
    "screen_set": {
        "calm": [
            "comes up to set the screen",
            "sets the pick",
            "screen set at the top",
            "the big man sets the screen",
        ],
        "building": [
            "sets a solid screen... {defender} fights through",
            "the pick is set... looking for the roll",
            "screen at the top... creates a gap",
            "sets the screen, rolls to the basket",
        ],
        "hype": [
            "SETS THE SCREEN! Opens it up!",
            "BIG screen! {defender} is caught!",
            "the pick creates a WIDE OPEN lane!",
            "screen and roll! HERE THEY GO!",
        ],
        "screaming": [
            "MASSIVE SCREEN! {DEFENDER} IS CAUGHT!",
            "THE PICK! WIDE OPEN!",
            "SCREEN AND ROLL! NOBODY HOME!",
            "SETS THE SCREEN! {DEFENDER} CAN'T GET THROUGH!",
        ],
    },
    "switch": {
        "calm": [
            "they switch",
            "switch on the screen",
            "the defense switches",
        ],
        "building": [
            "they switch... possible mismatch",
            "the defense switches... look at the size difference",
            "switch! That's a mismatch",
        ],
        "hype": [
            "SWITCH! That's a MISMATCH!",
            "they have to switch! Mismatch alert!",
            "the switch gives him a smaller defender!",
        ],
        "screaming": [
            "SWITCH! HUGE MISMATCH!",
            "THEY SWITCHED! THIS IS TROUBLE!",
            "THE SWITCH! {DEFENDER} CAN'T GUARD HIM!",
        ],
    },
}


def get_screen_clauses(screen_type: str, band: str) -> list[str]:
    """Get screen clauses for a given type and intensity."""
    key = "switch" if "switch" in screen_type.lower() else "screen_set"
    return SCREEN_CLAUSES[key].get(band, SCREEN_CLAUSES[key]["calm"])
