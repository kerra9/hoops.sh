"""Clause bank for shot attempt and result events."""

from hoops_sim.narration.clause_banks import ClauseBank

SHOT_MADE: ClauseBank = {
    "generic_make": {
        "calm": [
            "hits the shot",
            "knocks it down",
            "good from there",
            "puts it in",
            "the shot is good",
            "finds the bottom of the net",
            "converts",
            "buries the jumper",
        ],
        "building": [
            "hits the shot... that's a tough one",
            "knocks down the jumper... nothing but net",
            "drains it from {zone}",
            "the shot falls... count it",
            "buries it! Good shooting",
            "hits the tough shot over {defender}",
            "money from {zone}... nets it",
            "gets it to go... nice shot",
        ],
        "hype": [
            "DRAINS IT!",
            "BANG! It's good!",
            "HITS the shot! What a bucket!",
            "KNOCKS IT DOWN! Big shot!",
            "BURIES IT from {zone}!",
            "SWISH! Nothing but the bottom!",
            "COUNTS IT! Tough shot!",
            "GOT IT! What a shot!",
        ],
        "screaming": [
            "DRAINS IT! WHAT A SHOT!",
            "BANG! BANG! FROM {ZONE}!",
            "SWISH! NOTHING BUT NET!",
            "MONEY! ABSOLUTELY MONEY!",
            "HE CAN'T MISS! DRAINS ANOTHER ONE!",
            "BURIES IT! COLD-BLOODED!",
            "IT'S GOOD! IT'S GOOD! WHAT A SHOT!",
            "KNOCKS IT DOWN! ARE YOU KIDDING ME?!",
        ],
    },
}

SHOT_MISSED: ClauseBank = {
    "generic_miss": {
        "calm": [
            "no good",
            "misses the shot",
            "off the mark",
            "won't go",
            "rimmed out",
            "the shot is off",
            "can't get it to fall",
            "in and out",
        ],
        "building": [
            "no good... off the rim",
            "misses the shot... tough look",
            "won't go... rimmed out",
            "the shot is off... {defender} got a hand on it",
            "can't convert... good defense by {defender}",
            "off the mark... just missed it",
            "hits the rim... bounces out",
            "the shot rattles out",
        ],
        "hype": [
            "NO! Off the rim!",
            "can't get it to go! Misses!",
            "OFF THE MARK! Tough break!",
            "WON'T GO! So close!",
            "misses! The defense held!",
            "no good! Rimmed out!",
            "CAN'T CONVERT! Just missed!",
            "the shot is off! He needed that one!",
        ],
        "screaming": [
            "NO GOOD! OFF THE RIM!",
            "CAN'T GET IT TO FALL! MISSES!",
            "OH NO! THAT WON'T GO!",
            "MISSES THE SHOT! HEARTBREAK!",
            "OFF THE MARK! SO CLOSE!",
            "RIMMED OUT! HE NEEDED THAT ONE!",
            "THE SHOT IS NO GOOD! CAN'T BELIEVE IT!",
            "WON'T GO! THE RIM SAYS NO!",
        ],
    },
}

THREE_POINTER_MADE: ClauseBank = {
    "three_make": {
        "calm": [
            "hits the three",
            "three-pointer is good",
            "from downtown... good",
            "the three-ball goes in",
            "connects from deep",
            "nails the three",
            "three-pointer, good",
            "from beyond the arc... hits it",
        ],
        "building": [
            "hits the three-pointer... big shot",
            "from downtown... BANG!",
            "the three is good... nothing but net",
            "connects from deep... what a shot",
            "nails the three-pointer... count it",
            "three-ball... MONEY",
            "from beyond the arc... SWISH",
            "the long-range three... good!",
        ],
        "hype": [
            "DRAINS THE THREE!",
            "FROM DOWNTOWN! BANG!",
            "THREE-POINTER! MONEY!",
            "HITS THE THREE! What a shot!",
            "SPLASH! From deep!",
            "THE THREE-BALL IS GOOD!",
            "KNOCKS DOWN THE THREE!",
            "FROM WAY DOWNTOWN! GOT IT!",
        ],
        "screaming": [
            "THREE-POINTER! BANG! BANG!",
            "FROM DOWNTOWN! ARE YOU KIDDING ME?!",
            "THE THREE! THE THREE! NOTHING BUT NET!",
            "DRAINS THE LONG-RANGE THREE! UNBELIEVABLE!",
            "SPLASH! FROM DEEP! HE CAN'T MISS!",
            "THREE-POINTER! WHAT A SHOT! MY GOODNESS!",
            "THE DEEP THREE! ABSOLUTELY MONEY!",
            "FROM WAY DOWNTOWN! HE'S ON FIRE!",
        ],
    },
}

DUNK: ClauseBank = {
    "dunk": {
        "calm": [
            "finishes with a dunk",
            "throws it down",
            "slams it home",
            "dunks it",
            "flushes it",
            "puts it through with authority",
            "hammers it home",
            "finishes above the rim",
        ],
        "building": [
            "THROWS IT DOWN!",
            "slams it home with authority!",
            "rises up and dunks it!",
            "hammers it through the rim!",
            "powerful dunk! Rattled the rim!",
            "finishes with a FLUSH!",
            "rises and JAMS it!",
            "throws it down with two hands!",
        ],
        "hype": [
            "THROWS IT DOWN! What a slam!",
            "OH! SLAMS IT HOME!",
            "MONSTER JAM! The rim is shaking!",
            "HAMMERS IT! With authority!",
            "POWERFUL FLUSH! The crowd is on its feet!",
            "JAMS IT THROUGH! Wow!",
            "THUNDEROUS DUNK!",
            "RISES UP AND THROWS IT DOWN!",
        ],
        "screaming": [
            "THROWS IT DOWN! OH MY GOODNESS!",
            "MONSTER DUNK! THE RIM IS STILL SHAKING!",
            "POSTERIZED! WHAT A SLAM!",
            "OH WHAT A JAM! ARE YOU KIDDING ME?!",
            "THROWS IT DOWN WITH AUTHORITY! LOOK AT HIM!",
            "ABSOLUTELY DESTROYS THE RIM!",
            "THE HAMMER! THE EXCLAMATION POINT!",
            "WITH NO REGARD FOR HUMAN LIFE! WHAT A DUNK!",
        ],
    },
}


def get_shot_clauses(
    made: bool, is_three: bool, is_dunk: bool, band: str,
) -> list[str]:
    """Get shot clauses based on result, type, and intensity."""
    if is_dunk and made:
        return DUNK["dunk"].get(band, DUNK["dunk"]["calm"])
    if is_three and made:
        return THREE_POINTER_MADE["three_make"].get(
            band, THREE_POINTER_MADE["three_make"]["calm"],
        )
    if made:
        return SHOT_MADE["generic_make"].get(
            band, SHOT_MADE["generic_make"]["calm"],
        )
    return SHOT_MISSED["generic_miss"].get(
        band, SHOT_MISSED["generic_miss"]["calm"],
    )
