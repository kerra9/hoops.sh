"""Clause bank for dribble move events.

Organized by move_type x intensity_band.
{defender} and {DEFENDER} are template variables replaced at generation time.
"""

from hoops_sim.narration.clause_banks import ClauseBank

CROSSOVER: ClauseBank = {
    "crossover": {
        "calm": [
            "crosses over",
            "with the crossover",
            "hits the cross on {defender}",
            "little crossover",
            "quick cross right to left",
            "changes direction with the crossover",
            "cross dribble, probing",
            "shifts the ball with a cross",
        ],
        "building": [
            "snaps the crossover on {defender}",
            "crosses {defender} up... gets a step",
            "crossover, {defender} bites",
            "quick cross, {defender} reaching",
            "crossover sends {defender} leaning",
            "sharp crossover... step created",
            "the crossover catches {defender} flat-footed",
            "cross, change of speed, a step ahead now",
        ],
        "hype": [
            "CROSSES {defender}! Gets a step!",
            "the crossover sends {defender} stumbling!",
            "crossover and {defender} is on his heels!",
            "crosses {defender} up! Look at that separation!",
            "wicked crossover! {defender} can't keep up!",
            "snaps the cross and {defender} is done!",
            "the handle! {defender} had no answer!",
            "crossed {defender} right out of his shoes!",
        ],
        "screaming": [
            "THE CROSSOVER! {DEFENDER} IS DONE!",
            "BREAKS {DEFENDER} with the cross!",
            "FILTHY crossover! {DEFENDER} had NO CHANCE!",
            "THE HANDLE IS DISGUSTING! {DEFENDER} IS LOST!",
            "OH THE CROSSOVER! LOOK AT {DEFENDER}!",
            "CROSSED {DEFENDER} INTO NEXT WEEK!",
            "ANKLE BREAKER! {DEFENDER} IS ON THE FLOOR!",
            "ABSOLUTELY FILTHY! THE CROSSOVER SENDS {DEFENDER} DOWN!",
        ],
    },
}

HESITATION: ClauseBank = {
    "hesitation": {
        "calm": [
            "with the hesitation",
            "hesi... keeps his dribble",
            "little hesi move",
            "pump fake with the dribble",
            "freeze dribble",
            "hesitation, feeling out {defender}",
            "quick hesi, looking for space",
            "little stutter step",
        ],
        "building": [
            "hesi... {defender} bites!",
            "hesitation gets {defender} on his heels",
            "the hesi freezes {defender}",
            "hesi move, creates just enough space",
            "hesitation... {defender} lunges!",
            "the hesi catches {defender} leaning",
            "stutter step... space created",
            "the hesitation opens up a lane",
        ],
        "hype": [
            "the hesi FREEZES {defender}!",
            "hesitation! {defender} is lost!",
            "hesi move, {defender} bites HARD!",
            "the hesitation is NASTY! Step created!",
            "look at the hesi! {defender} took the bait!",
            "DISGUSTING hesitation move!",
            "the hesi had {defender} on skates!",
            "pump, hesi, GO! {defender} can't recover!",
        ],
        "screaming": [
            "THE HESI! {DEFENDER} IS FROZEN!",
            "LOOK AT THAT HESITATION! {DEFENDER} IS DONE!",
            "THE FILTHIEST HESI YOU WILL EVER SEE!",
            "HESITATION! {DEFENDER} WENT TO THE WRONG ZIP CODE!",
            "OH MY! THE HESI! {DEFENDER} IS SHOOK!",
            "NASTY HESITATION! {DEFENDER} ON THE GROUND!",
            "THE HESI SENT {DEFENDER} TO ANOTHER DIMENSION!",
            "ABSOLUTELY DISGUSTING HESITATION MOVE!",
        ],
    },
}

STEP_BACK: ClauseBank = {
    "step_back": {
        "calm": [
            "step-back",
            "creates space with the step-back",
            "backs away with a step",
            "subtle step-back to create room",
            "step-back, keeps his balance",
            "little step-back off the dribble",
            "retreating dribble into space",
            "side-step to create the look",
        ],
        "building": [
            "step-back... space created",
            "the step-back gives him room to work",
            "step-back, {defender} can't close",
            "step-back leaves {defender} a step behind",
            "smooth step-back... looking at the rim now",
            "the step-back creates daylight",
            "gathers, step-back, has the space",
            "textbook step-back, {defender} stuck",
        ],
        "hype": [
            "step-back! Wide open!",
            "the step-back creates ACRES of space!",
            "step-back three! {defender} can't contest!",
            "STEP-BACK! {defender} is too far away!",
            "that step-back is MONEY!",
            "gorgeous step-back! Clean look!",
            "the step-back leaves {defender} grasping at air!",
            "step-back jumper! Nobody is close!",
        ],
        "screaming": [
            "THE STEP-BACK! THAT'S HIS MOVE!",
            "STEP-BACK THREE! {DEFENDER} HAD NO CHANCE!",
            "YOU KNOW IT'S COMING AND YOU STILL CAN'T STOP IT!",
            "THE PATENTED STEP-BACK! MONEY!",
            "STEP-BACK! PURE SEPARATION! NOTHING {DEFENDER} CAN DO!",
            "THAT STEP-BACK IS UNGUARDABLE!",
            "THE STEP-BACK! NOBODY DOES IT BETTER!",
            "STEP-BACK FROM DEEP! {DEFENDER} IS HELPLESS!",
        ],
    },
}

BEHIND_THE_BACK: ClauseBank = {
    "behind_the_back": {
        "calm": [
            "behind the back",
            "slips it behind his back",
            "quick behind-the-back move",
            "behind the back to switch hands",
            "behind-the-back dribble",
            "wraps it around his back",
            "tucks it behind the back",
            "BTB to change direction",
        ],
        "building": [
            "behind the back... {defender} off-balance",
            "behind the back, creates an angle",
            "slick behind-the-back move on {defender}",
            "behind the back and he's by {defender}",
            "BTB... that opened things up",
            "behind the back, new lane created",
            "crafty behind-the-back, {defender} reaching",
            "behind the back and past {defender}",
        ],
        "hype": [
            "behind the back! {defender} is lost!",
            "the BTB move leaves {defender} spinning!",
            "behind the back! Pure filth!",
            "look at the behind-the-back! {defender} had no answer!",
            "behind the back move! SO SMOOTH!",
            "BTB and he's GONE past {defender}!",
            "the behind-the-back is NASTY!",
            "wraps it behind his back and {defender} can only watch!",
        ],
        "screaming": [
            "BEHIND THE BACK! {DEFENDER} IS DONE!",
            "THE BTB! ABSOLUTELY FILTHY!",
            "BEHIND THE BACK SNATCHBACK! {DEFENDER} KISSES THE GROUND!",
            "OH THE BEHIND-THE-BACK! DISGUSTING!",
            "BTB MOVE! {DEFENDER} IS ON SKATES!",
            "THE BEHIND THE BACK! LOOK AT THIS!",
            "WHAT A MOVE! BEHIND THE BACK! {DEFENDER} IS LOST!",
            "BEHIND THE BACK! CRIMINAL HANDLE!",
        ],
    },
}

SPIN_MOVE: ClauseBank = {
    "spin_move": {
        "calm": [
            "spins",
            "spin move",
            "quick spin off {defender}",
            "uses the spin dribble",
            "pivots with the spin",
            "spins baseline",
            "spin move, keeps his dribble",
            "tight spin move",
        ],
        "building": [
            "spins past {defender}",
            "the spin move creates space",
            "spin... gets around {defender}",
            "smooth spin, {defender} a step behind",
            "the spin move beats {defender}",
            "spins off the contact... keeps going",
            "spin move and he's free",
            "full spin, {defender} can't keep up",
        ],
        "hype": [
            "SPINS past {defender}!",
            "the spin move is TOO QUICK for {defender}!",
            "360 spin! {defender} is lost!",
            "spin move! Clean! Past {defender}!",
            "the spin leaves {defender} grabbing air!",
            "spinning past {defender} like he's not there!",
            "SICK spin move! Wide open!",
            "spins and {defender} is LEFT IN THE DUST!",
        ],
        "screaming": [
            "THE SPIN! {DEFENDER} HAD NO CHANCE!",
            "360 SPIN MOVE! ABSOLUTELY FILTHY!",
            "HE SPUN {DEFENDER} RIGHT INTO THE GROUND!",
            "THE SPIN MOVE! {DEFENDER} IS DIZZY!",
            "SPINNING! {DEFENDER} DOESN'T KNOW WHERE HE WENT!",
            "WHAT A SPIN MOVE! {DEFENDER} IS DONE!",
            "THE SPIN! PURE ARTISTRY! {DEFENDER} IS LOST!",
            "DEVASTATING SPIN MOVE! {DEFENDER} HAD NO ANSWER!",
        ],
    },
}

# Combined bank for easy lookup
DRIBBLE_CLAUSE_BANKS: dict[str, ClauseBank] = {
    "crossover": CROSSOVER,
    "hesitation": HESITATION,
    "step_back": STEP_BACK,
    "behind_the_back": BEHIND_THE_BACK,
    "behind_the_back_snatchback": BEHIND_THE_BACK,
    "spin_move": SPIN_MOVE,
    "spin": SPIN_MOVE,
    "jab_step": HESITATION,  # jab step uses hesitation bank
}


def get_dribble_clauses(
    move_type: str, band: str,
) -> list[str]:
    """Get clauses for a dribble move type at an intensity band."""
    bank = DRIBBLE_CLAUSE_BANKS.get(move_type)
    if bank is None:
        # Fall back to crossover for unknown move types
        bank = CROSSOVER
    # Get the inner dict (first value in the bank)
    inner = next(iter(bank.values()))
    return inner.get(band, inner.get("calm", []))
