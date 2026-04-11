"""Clause bank for pass events."""

from hoops_sim.narration.clause_banks import ClauseBank

PASS_CLAUSES: ClauseBank = {
    "pass": {
        "calm": [
            "passes to {receiver}",
            "swings it to {receiver}",
            "finds {receiver}",
            "dishes to {receiver}",
            "moves the ball to {receiver}",
            "hits {receiver} with the pass",
            "ball goes to {receiver}",
            "over to {receiver}",
        ],
        "building": [
            "finds {receiver} on the wing",
            "kicks it out to {receiver}",
            "swings it... {receiver} catches in rhythm",
            "beautiful pass to {receiver}",
            "thread-the-needle pass to {receiver}",
            "skip pass to {receiver}... open!",
            "hits {receiver} in stride",
            "delivers the pass to {receiver}",
        ],
        "hype": [
            "FINDS {receiver} WIDE OPEN!",
            "kicks it out! {receiver} catches and shoots!",
            "BEAUTIFUL PASS! {receiver} has it!",
            "the pass! {receiver} is ALL ALONE!",
            "skip pass to {receiver}! OPEN LOOK!",
            "THREADS THE NEEDLE to {receiver}!",
            "DISH! {receiver} ready to fire!",
            "what a FIND! {receiver} in the corner!",
        ],
        "screaming": [
            "THE PASS! {RECEIVER} IS WIDE OPEN!",
            "KICKS IT OUT! {RECEIVER}! OPEN!",
            "INCREDIBLE PASS! {RECEIVER} ALL ALONE!",
            "THREAD THE NEEDLE! {RECEIVER} CATCHES!",
            "THE DISH! {RECEIVER} READY TO GO!",
            "BEAUTIFUL! {RECEIVER} HAS THE OPEN LOOK!",
            "SKIP PASS! {RECEIVER}! NOBODY ON HIM!",
            "WHAT A FIND! {RECEIVER} IN RHYTHM!",
        ],
    },
}


def get_pass_clauses(band: str) -> list[str]:
    """Get pass clauses at an intensity band."""
    return PASS_CLAUSES["pass"].get(band, PASS_CLAUSES["pass"]["calm"])
