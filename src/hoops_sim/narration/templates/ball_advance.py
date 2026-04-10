"""Ball advance templates -- bringing the ball up court."""

from __future__ import annotations

TRANSITION_PUSH_TEMPLATES = [
    "{handler} pushes it ahead in transition!",
    "{handler} races up the floor, looking for numbers!",
    "{handler} grabs it and goes! Fast break!",
    "{handler} outlets ahead, pushing the pace.",
    "Here comes {handler}, pushing in transition!",
    "{handler} takes off with the ball, looking to run!",
    "{handler} leads the break, three on two!",
    "{handler} sprints up court, {team} in transition!",
]

WALK_IT_UP_TEMPLATES = [
    "{handler} brings it up slowly. {team} sets up the half-court offense.",
    "{handler} walks it up, surveys the defense.",
    "{handler} brings the ball across halfcourt. {play} coming.",
    "{handler} takes his time. {team} gets organized.",
    "{handler} dribbles up court, no rush.",
    "{handler} brings it up for {team}.",
    "{handler} crosses halfcourt, calls out the set.",
    "{handler} at the top of the key, directing traffic.",
]

AFTER_TIMEOUT_TEMPLATES = [
    "{handler} inbounds to {receiver} after the timeout. {team} runs their set.",
    "Coming out of the timeout, {handler} brings it up for {team}.",
    "{team} back from the timeout. {handler} has the ball.",
    "After the break, {handler} sets up the offense for {team}.",
]

AFTER_MADE_BASKET_TEMPLATES = [
    "{handler} inbounds quickly, {team} looking to answer.",
    "{handler} takes it out, pushes it up for {team}.",
    "{handler} gets the inbound and brings it up.",
    "{team} needs a bucket here. {handler} brings it up.",
]
