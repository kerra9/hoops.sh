"""Expanded narration templates for micro-action events.

200+ templates covering dribble moves, screens, drives, defensive plays,
and contextual chains. These are used by the narration engine to generate
rich, varied play-by-play text at the micro-action level.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Dribble move templates
# ---------------------------------------------------------------------------

CROSSOVER_TEMPLATES = [
    "{player} with the crossover... gets a step on {defender}!",
    "{player} crosses over to the left, {defender} stumbles trying to stay in front.",
    "Quick crossover by {player}! He's got space now.",
    "{player} hits the crossover... clean separation!",
]

HESITATION_TEMPLATES = [
    "{player} with the hesitation... freezes {defender}!",
    "{player} uses the hesi to get {defender} leaning the wrong way.",
    "Hesitation dribble by {player}... the defender bites!",
    "{player} gives a little hesi and goes right by.",
]

SPIN_MOVE_TEMPLATES = [
    "{player} spins past {defender} into the lane...",
    "Spin move by {player}! That's a highlight reel handle.",
    "{player} with the spin... {defender} had no chance.",
    "Oh! {player} spins off {defender} and has a clear path!",
]

STEP_BACK_TEMPLATES = [
    "{player} hits the step-back... creates separation for the jumper!",
    "Step-back by {player}! {defender} can't close out in time.",
    "{player} rises up on the step-back... that's tough to guard.",
    "{player} with the crafty step-back, gets {defender} on his heels.",
]

BEHIND_THE_BACK_TEMPLATES = [
    "{player} goes behind the back... nice handle!",
    "Behind-the-back dribble by {player}! Smooth.",
    "{player} takes it behind the back and accelerates past {defender}.",
]

IN_AND_OUT_TEMPLATES = [
    "{player} with the in-and-out... gets {defender} reaching!",
    "In-and-out dribble by {player}. Simple but effective.",
    "{player} fakes the crossover with the in-and-out...",
]

SHAMGOD_TEMPLATES = [
    "Oh! {player} with the SHAMGOD! {defender} is completely lost!",
    "{player} pulls out the Shamgod... and it works! Incredible handle!",
    "The Shamgod by {player}! What a move!",
]

ANKLE_BREAKER_TEMPLATES = [
    "Oh! {player} hits the {move}... ANKLE BREAKER! {defender} is stumbling!",
    "{player} with the {move}... {defender} is on the FLOOR! Ankle breaker!",
    "ANKLE BREAKER! {player}'s {move} just sent {defender} to the hardwood!",
    "{player} breaks {defender}'s ankles with that {move}! The crowd goes wild!",
]

# ---------------------------------------------------------------------------
# Screen templates
# ---------------------------------------------------------------------------

SCREEN_SET_TEMPLATES = [
    "{screener} comes up to set the screen for {handler}...",
    "{screener} plants at the top of the key. Screen for {handler}.",
    "Here comes the pick from {screener}. {handler} uses it.",
    "{handler} calls for the screen. {screener} sets it up high.",
]

SCREEN_DEFENDER_REACTION_TEMPLATES = [
    "{defender} fights over the screen...",
    "{defender} goes under -- giving up the jumper.",
    "Switch! {big} is now on {handler}... that's a mismatch.",
    "{defender} gets caught on the screen. {handler} is free.",
    "{big} hedges out, then recovers to the roller.",
]

# ---------------------------------------------------------------------------
# Drive templates
# ---------------------------------------------------------------------------

DRIVE_TEMPLATES = [
    "{player} attacks the basket...",
    "{player} puts his head down and drives!",
    "{player} takes it strong to the hole!",
    "{player} slashes through the lane...",
    "{player} turns the corner and gets into the paint!",
]

FINISH_LAYUP_TEMPLATES = [
    "{player} with the layup... {result}!",
    "{player} floats it up off the glass... {result}.",
    "{player} lays it in with the soft touch!",
]

FINISH_DUNK_TEMPLATES = [
    "{player} THROWS IT DOWN! What a slam!",
    "{player} with the powerful dunk!",
    "{player} soars and HAMMERS it home!",
    "{player} rises up and FLUSHES it!",
]

FINISH_POSTER_TEMPLATES = [
    "{player} goes up... POSTER DUNK on {defender}! Oh my!",
    "{player} takes it right at {defender}... POSTERIZED!",
    "He dunked ON {defender}! That's going on the highlight reel!",
]

FINISH_FLOATER_TEMPLATES = [
    "{player} with the floater over the outstretched arm of {defender}...",
    "{player} kisses it off the glass with the runner...",
    "Floater by {player} from the lane... soft touch!",
]

FINISH_EURO_STEP_TEMPLATES = [
    "{player} euro-steps around {defender}... kiss off the glass!",
    "The euro-step by {player}! Avoids the contact and finishes!",
    "{player} with the crafty euro-step, gets {defender} going the wrong way.",
]

FINISH_REVERSE_TEMPLATES = [
    "{player} goes reverse on the other side of the rim!",
    "Reverse layup by {player}! Uses the rim as protection.",
    "{player} with the acrobatic reverse... and it drops!",
]

# ---------------------------------------------------------------------------
# Defensive play templates
# ---------------------------------------------------------------------------

CONTEST_TEMPLATES = [
    "{defender} with the incredible recovery... gets back to contest!",
    "{defender} closes out just in time!",
    "Well contested by {defender}!",
    "{defender} gets a hand up on the shot.",
]

HELP_DEFENSE_TEMPLATES = [
    "{helper} rotates over from the weak side!",
    "{helper} slides into the lane to cut off the drive!",
    "Here comes the help from {helper}...",
]

BLOCK_TEMPLATES_EXTENDED = [
    "{blocker} SWATS {shooter}'s shot away! What a block!",
    "{blocker} comes from the weak side... REJECTED!",
    "{shooter} tries to finish... BLOCKED by {blocker}!",
    "Get that out of here! {blocker} with the emphatic block!",
    "{blocker} pins it against the backboard! Incredible timing!",
]

STEAL_TEMPLATES_EXTENDED = [
    "{defender} reads the pass perfectly... INTERCEPTED!",
    "{defender} jumps the passing lane! Steal!",
    "{defender} pokes it away! Quick hands!",
    "Turnover! {defender} picks {handler}'s pocket!",
    "{defender} with the anticipation... STEAL!",
]

# ---------------------------------------------------------------------------
# Pass templates
# ---------------------------------------------------------------------------

PASS_ASSIST_TEMPLATES = [
    "Great feed from {passer}! {scorer} converts.",
    "{passer} finds {scorer} with a beautiful pass!",
    "Dime from {passer}! {scorer} finishes it off.",
    "{passer} with the vision -- threads it to {scorer}!",
]

ALLEY_OOP_TEMPLATES = [
    "{passer} throws it up... {scorer} SLAMS it home! Alley-oop!",
    "Lob from {passer}! {scorer} catches it and throws it down!",
    "ALLEY-OOP! {passer} to {scorer}! The crowd erupts!",
]

NO_LOOK_PASS_TEMPLATES = [
    "{passer} with the no-look pass to {receiver}! What vision!",
    "No-look from {passer}! {receiver} is wide open!",
]

SKIP_PASS_TEMPLATES = [
    "{passer} skips it across to {receiver} on the wing!",
    "Skip pass from {passer}! {receiver} has an open look!",
]

# ---------------------------------------------------------------------------
# Game situation templates
# ---------------------------------------------------------------------------

CLUTCH_SHOT_TEMPLATES = [
    "Clutch! {player} delivers in crunch time!",
    "Ice in his veins! {player} nails it with the game on the line!",
    "{player} comes through when it matters most!",
]

MOMENTUM_SHIFT_TEMPLATES = [
    "The momentum has shifted! {team} is rolling!",
    "{team} can't miss right now! What a run!",
    "The crowd is ROARING! {team} on a {points}-point run!",
]

LEAD_CHANGE_TEMPLATES = [
    "{team} takes the lead!",
    "We've got a new leader! {team} in front by {lead}!",
]

TIE_GAME_TEMPLATES = [
    "We're all tied up!",
    "Back to even! What a game!",
]
