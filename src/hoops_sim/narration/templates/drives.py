"""Drive and finishing templates."""

from __future__ import annotations

DRIVE_INITIATION_TEMPLATES = [
    "{player} attacks the basket!",
    "{player} puts his head down and drives!",
    "{player} takes it strong to the hole!",
    "{player} slashes through the lane...",
    "{player} turns the corner and gets into the paint!",
    "{player} drives baseline!",
    "{player} blows by {defender} and gets to the rim!",
    "{player} explodes to the basket!",
]

LAYUP_MADE_TEMPLATES = [
    "{player} with the layup... got it!",
    "{player} floats it up off the glass... good!",
    "{player} lays it in with the soft touch!",
    "{player} finishes at the rim!",
    "{player} scoops it in!",
    "{player} kisses it off the glass!",
]

LAYUP_MISSED_TEMPLATES = [
    "{player} with the layup... in and out!",
    "{player} tries to finish... rimmed out.",
    "{player} can't get it to fall at the rim.",
    "{player} with the layup attempt... no good.",
]

DUNK_TEMPLATES = [
    "{player} THROWS IT DOWN! What a slam!",
    "{player} with the powerful dunk!",
    "{player} soars and HAMMERS it home!",
    "{player} rises up and FLUSHES it!",
    "{player} gets UP for the dunk!",
    "{player} with the one-handed flush!",
    "{player} SLAMS it through!",
]

POSTER_DUNK_TEMPLATES = [
    "{player} goes up... POSTER on {defender}! Oh my!",
    "{player} takes it right at {defender}... POSTERIZED!",
    "He dunked ON {defender}! That's a highlight!",
    "{player} with NO REGARD for {defender}! POSTER!",
]

FLOATER_TEMPLATES = [
    "{player} with the floater over {defender}...",
    "{player} kisses it off the glass with the runner...",
    "Floater by {player} from the lane... soft touch!",
    "{player} with the tear-drop floater...",
    "{player} puts up the runner in the lane...",
]

EURO_STEP_TEMPLATES = [
    "{player} euro-steps around {defender}!",
    "The euro-step by {player}! Avoids the contact and finishes!",
    "{player} with the crafty euro-step, {defender} going the wrong way.",
    "{player} uses the euro-step, gets to the other side of the rim.",
]

REVERSE_LAYUP_TEMPLATES = [
    "{player} goes reverse on the other side of the rim!",
    "Reverse layup by {player}! Uses the rim as protection.",
    "{player} with the acrobatic reverse... and it drops!",
    "{player} finishes with the reverse!",
]

FINGER_ROLL_TEMPLATES = [
    "{player} with the finger roll at the rim!",
    "{player} extends and rolls it off the fingers!",
    "Soft finger roll by {player}...",
]

HELP_DEFENSE_ON_DRIVE_TEMPLATES = [
    "Here comes the help from {helper}!",
    "{helper} rotates over to cut off the drive!",
    "{helper} slides over from the weak side!",
    "The help defense collapses on {driver}!",
]

KICK_OUT_FROM_DRIVE_TEMPLATES = [
    "{driver} draws the defense and kicks it out to {receiver}!",
    "{driver} sees {receiver} open and dishes it!",
    "The defense collapses... {driver} finds {receiver} on the perimeter!",
    "{driver} draws two and kicks to {receiver}!",
]

FINISH_TEMPLATES_BY_TYPE = {
    "layup": (LAYUP_MADE_TEMPLATES, LAYUP_MISSED_TEMPLATES),
    "dunk": (DUNK_TEMPLATES, DUNK_TEMPLATES),  # dunks rarely miss in narration
    "floater": (FLOATER_TEMPLATES, FLOATER_TEMPLATES),
    "euro_step": (EURO_STEP_TEMPLATES, EURO_STEP_TEMPLATES),
    "reverse": (REVERSE_LAYUP_TEMPLATES, REVERSE_LAYUP_TEMPLATES),
    "finger_roll": (FINGER_ROLL_TEMPLATES, FINGER_ROLL_TEMPLATES),
}
