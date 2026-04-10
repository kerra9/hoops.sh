"""Dribble move templates -- per move type with success/fail variants."""

from __future__ import annotations

CROSSOVER_SUCCESS = [
    "{player} with the crossover... gets a step on {defender}!",
    "{player} crosses over to the left, {defender} stumbles.",
    "Quick crossover by {player}! He's got space.",
    "{player} hits the crossover... clean separation!",
    "{player} sizes up {defender} and crosses over. He's by him.",
]

CROSSOVER_FAIL = [
    "{player} tries the crossover but {defender} stays in front.",
    "{player} with the cross... {defender} reads it perfectly.",
    "Crossover by {player}, but {defender} doesn't bite.",
]

HESITATION_SUCCESS = [
    "{player} with the hesitation... freezes {defender}!",
    "{player} uses the hesi, {defender} leans the wrong way.",
    "Hesitation by {player}... the defender bites!",
    "{player} gives a little hesi and blows by.",
    "{player} with the stop-and-go, creates a sliver of daylight.",
]

HESITATION_FAIL = [
    "{player} tries the hesi, {defender} doesn't budge.",
    "Hesitation dribble by {player}, but {defender} stays disciplined.",
]

SPIN_MOVE_SUCCESS = [
    "{player} spins past {defender} into the lane...",
    "Spin move by {player}! That's a highlight handle.",
    "{player} with the spin... {defender} had no chance.",
    "Oh! {player} spins off {defender} and has a clear path!",
    "{player} executes the spin move beautifully, gets into the paint.",
]

SPIN_MOVE_FAIL = [
    "{player} tries the spin... {defender} stays attached.",
    "Spin move by {player}, but he loses the handle slightly.",
    "{player} with the spin, {defender} stays disciplined.",
]

STEP_BACK_SUCCESS = [
    "{player} hits the step-back... creates separation for the jumper!",
    "Step-back by {player}! {defender} can't close out in time.",
    "{player} rises on the step-back... tough to guard.",
    "{player} with the crafty step-back, {defender} on his heels.",
    "{player} jabs, step-back... he's got all the room he needs.",
]

STEP_BACK_FAIL = [
    "{player} with the step-back, but {defender} stays right with him.",
    "{player} tries to create with the step-back, not much room.",
]

BEHIND_THE_BACK_SUCCESS = [
    "{player} goes behind the back... nice handle!",
    "Behind-the-back by {player}! Smooth.",
    "{player} takes it behind the back and accelerates past {defender}.",
    "{player} with the behind-the-back... that's elite ball-handling.",
]

BEHIND_THE_BACK_FAIL = [
    "{player} tries the behind-the-back, almost loses it.",
    "Behind-the-back by {player}, but {defender} recovers quickly.",
]

IN_AND_OUT_SUCCESS = [
    "{player} with the in-and-out... gets {defender} reaching!",
    "In-and-out dribble by {player}. Simple but effective.",
    "{player} fakes the crossover with the in-and-out... free!",
    "{player} sells the in-and-out, creates just enough space.",
]

IN_AND_OUT_FAIL = [
    "{player} tries the in-and-out, {defender} reads it.",
    "In-and-out by {player}, but {defender} doesn't bite.",
]

SHAMGOD_SUCCESS = [
    "Oh! {player} with the SHAMGOD! {defender} is completely lost!",
    "{player} pulls out the Shamgod... incredible handle!",
    "The Shamgod by {player}! What a move!",
    "{player} hits the Shamgod and the crowd goes wild!",
]

SHAMGOD_FAIL = [
    "{player} tries the Shamgod... a little too fancy there.",
    "The Shamgod attempt by {player} almost goes wrong.",
]

BETWEEN_THE_LEGS_SUCCESS = [
    "{player} goes between the legs, shifts direction!",
    "Between the legs by {player}, changes pace and direction.",
    "{player} with the between-the-legs combo, gets some space.",
]

BETWEEN_THE_LEGS_FAIL = [
    "{player} with the between-the-legs, {defender} stays home.",
]

SNATCH_BACK_SUCCESS = [
    "{player} hits the snatch-back... creates a window!",
    "Snatch-back by {player}! Quick change of direction.",
    "{player} with the snatch-back dribble, {defender} lunges forward.",
]

SNATCH_BACK_FAIL = [
    "{player} tries the snatch-back, not enough separation.",
]

HARDEN_STEP_BACK_SUCCESS = [
    "{player} with the Harden step-back! Big separation!",
    "{player} hits that patented step-back three-pointer move!",
    "The step-back from deep! {player} creating his own shot.",
]

HARDEN_STEP_BACK_FAIL = [
    "{player} tries the step-back but {defender} crowds him.",
]

ANKLE_BREAKER_TEMPLATES = [
    "Oh! {player} hits the {move}... ANKLE BREAKER! {defender} is stumbling!",
    "{player} with the {move}... {defender} is on the FLOOR! Ankle breaker!",
    "ANKLE BREAKER! {player}'s {move} just sent {defender} to the hardwood!",
    "{player} breaks {defender}'s ankles with that {move}! The crowd goes wild!",
    "Oh no! {defender} went down! {player}'s {move} was absolutely filthy!",
]

COMBO_CHAIN_TEMPLATES = [
    "{player} chains the moves together... {defender} can't keep up!",
    "{player} with the combo dribble... creating his own shot.",
    "Back-to-back moves by {player}, the defense is scrambling.",
    "{player} is cooking! Another move in the combo.",
]

# Map move types to their template lists
DRIBBLE_TEMPLATES_BY_TYPE = {
    "crossover": (CROSSOVER_SUCCESS, CROSSOVER_FAIL),
    "hesitation": (HESITATION_SUCCESS, HESITATION_FAIL),
    "spin_move": (SPIN_MOVE_SUCCESS, SPIN_MOVE_FAIL),
    "step_back": (STEP_BACK_SUCCESS, STEP_BACK_FAIL),
    "behind_the_back": (BEHIND_THE_BACK_SUCCESS, BEHIND_THE_BACK_FAIL),
    "in_and_out": (IN_AND_OUT_SUCCESS, IN_AND_OUT_FAIL),
    "shamgod": (SHAMGOD_SUCCESS, SHAMGOD_FAIL),
    "between_the_legs": (BETWEEN_THE_LEGS_SUCCESS, BETWEEN_THE_LEGS_FAIL),
    "snatch_back": (SNATCH_BACK_SUCCESS, SNATCH_BACK_FAIL),
    "harden_step_back": (HARDEN_STEP_BACK_SUCCESS, HARDEN_STEP_BACK_FAIL),
}
