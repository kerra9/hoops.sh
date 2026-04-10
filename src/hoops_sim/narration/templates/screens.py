"""Screen action templates -- PnR reads, coverage, rolls, pops."""

from __future__ import annotations

SCREEN_SET_TEMPLATES = [
    "{screener} comes up to set the screen for {handler}.",
    "{screener} plants at the top of the key. Screen for {handler}.",
    "Here comes the pick from {screener}. {handler} uses it.",
    "{handler} calls for the screen. {screener} sets it up high.",
    "{screener} sets a solid screen. {handler} comes off.",
    "Pick-and-roll with {handler} and {screener}.",
    "{handler} waits for the screen from {screener}... here it comes.",
    "{screener} walls off the defender. {handler} turns the corner.",
]

DEFENDER_GOES_OVER = [
    "{defender} fights over the screen, staying attached to {handler}.",
    "{defender} goes over the top, chasing {handler} around the pick.",
    "{defender} battles over {screener}'s screen.",
    "Good effort by {defender}, getting over the screen.",
]

DEFENDER_GOES_UNDER = [
    "{defender} goes under -- giving up the mid-range jumper.",
    "{defender} ducks under the screen. Conceding the pull-up.",
    "{defender} goes under, daring {handler} to shoot.",
    "Under the screen by {defender}. {handler} has space for the jumper.",
]

SWITCH_TEMPLATES = [
    "Switch! {big} is now on {handler}... that's a mismatch.",
    "They switch it. {big} picks up {handler}.",
    "The defense switches. {handler} has the smaller defender now.",
    "Switch on the screen. {big} trying to stay in front of {handler}.",
    "They switch everything. {handler} sees the mismatch.",
]

HEDGE_TEMPLATES = [
    "{big} hedges hard on the screen, then recovers.",
    "{big} steps out to contain {handler}, then gets back.",
    "Hard hedge by {big}! {handler} has to pull it back out.",
    "{big} shows high on the screen to slow {handler} down.",
]

DROP_COVERAGE_TEMPLATES = [
    "{big} drops back into the paint, protecting the rim.",
    "Drop coverage. {big} stays near the basket.",
    "{big} sags back, giving up the mid-range to protect the paint.",
    "They're dropping {big} on the pick-and-roll.",
]

ROLL_TEMPLATES = [
    "{screener} rolls hard to the basket!",
    "{screener} dives to the rim after the screen.",
    "{screener} rolls to the basket, looking for the lob.",
    "The roll man, {screener}, heading to the rim.",
    "{screener} finishes the screen and rolls downhill.",
]

POP_TEMPLATES = [
    "{screener} pops out to the three-point line!",
    "Instead of rolling, {screener} pops for the jumper.",
    "{screener} fades to the elbow after the screen.",
    "{screener} pops out. Open if {handler} can find him.",
]

SLIP_SCREEN_TEMPLATES = [
    "{screener} slips the screen early, cuts to the basket!",
    "{screener} fakes the screen and slips to the rim!",
    "The slip by {screener}! Catches the defense off guard.",
]
