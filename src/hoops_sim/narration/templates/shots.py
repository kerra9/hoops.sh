"""Shot result templates -- per zone, per result type."""

from __future__ import annotations

# Made shot templates by context
THREE_POINTER_MADE = [
    "{shooter} from downtown... BANG! The three is good!",
    "{shooter} pulls up from deep... DRAINS IT!",
    "{shooter} for three... GOT IT!",
    "{shooter} from beyond the arc... SWISH!",
    "{shooter} lets it fly from three... NOTHING BUT NET!",
    "{shooter} catches and fires... THREE-BALL! It's good!",
    "Three-pointer by {shooter}! {team} by {lead}.",
    "{shooter} from three... SPLASH!",
    "{shooter} knocks down the triple!",
    "{shooter} buries the three!",
]

CORNER_THREE_MADE = [
    "{shooter} from the corner... BANG! Three-pointer!",
    "{shooter} knocks it down from the corner!",
    "Corner three by {shooter}! It's good!",
    "{shooter} open in the corner... DRAINS IT!",
    "{shooter} from the short corner... three-ball!",
]

MID_RANGE_MADE = [
    "{shooter} pulls up from the mid-range... got it!",
    "{shooter} with the jumper from {zone}... good!",
    "{shooter} from the elbow... SWISH!",
    "{shooter} with the mid-range game... bucket!",
    "{shooter} rises and fires from {distance} feet... good!",
    "{shooter} with the pull-up jumper... money!",
]

CLOSE_RANGE_MADE = [
    "{shooter} finishes at the rim!",
    "{shooter} puts it in from close range!",
    "{shooter} with the easy bucket inside!",
    "{shooter} scores from {distance} feet out.",
]

# Missed shot templates
THREE_POINTER_MISSED = [
    "{shooter} fires from three... no good.",
    "{shooter} from deep... rimmed out.",
    "{shooter} for three... off the mark.",
    "{shooter} lets it fly from three... won't go.",
    "{shooter} from downtown... in and out!",
    "{shooter} with the three-pointer attempt... off the front rim.",
]

MID_RANGE_MISSED = [
    "{shooter} pulls up from {zone}... short.",
    "{shooter} with the jumper... no good.",
    "{shooter} fires from {distance} feet... off the mark.",
    "{shooter} from the mid-range... rimmed out.",
    "{shooter} with the contested jumper... won't go.",
]

CLOSE_RANGE_MISSED = [
    "{shooter} tries to finish... rimmed out.",
    "{shooter} at the rim... can't get it to fall.",
    "{shooter} with the attempt from close... no good.",
]

AIRBALL_TEMPLATES = [
    "{shooter} from {zone}... AIRBALL!",
    "{shooter} lets it fly... airball! Way off.",
    "Airball by {shooter}! The crowd lets him hear it.",
]

AND_ONE_SUFFIX = [
    " AND ONE! He's fouled on the play!",
    " And the foul! That's an and-one!",
    " Plus the foul! He got hit on the way up!",
    " AND THE FOUL! What a play!",
]

SWISH_ADJECTIVES = [
    "Nothing but net!",
    "Swish!",
    "Pure!",
    "Silky smooth!",
    "Clean!",
]

CONTESTED_SHOT_PREFIXES = [
    "Contested shot by",
    "With a hand in his face,",
    "Tough shot by",
    "Over the outstretched arm,",
    "Through the contact,",
]

OPEN_SHOT_PREFIXES = [
    "Wide open,",
    "All alone,",
    "Left open,",
    "Nobody near him,",
    "Good look for",
]

# Score update suffixes
SCORE_UPDATE_TEMPLATES = [
    "{team} leads {score}.",
    "That puts {team} up {lead}.",
    "Score is {home_team} {home_score}, {away_team} {away_score}.",
    "{team} by {lead}.",
]

TIE_SCORE_TEMPLATES = [
    "We're all tied up at {score}!",
    "Tied at {score}!",
    "It's knotted up, {score} apiece.",
]
