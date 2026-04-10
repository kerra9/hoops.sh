"""Dead ball narration templates -- free throws, substitutions, timeouts."""

from __future__ import annotations

FREE_THROW_MADE_TEMPLATES = [
    "{shooter} at the line... knocks it down.",
    "{shooter} from the stripe... good!",
    "{shooter} calmly sinks the free throw.",
    "Free throw good for {shooter}.",
]

FREE_THROW_MISSED_TEMPLATES = [
    "{shooter} at the line... no good.",
    "{shooter} misses the free throw.",
    "{shooter} from the stripe... off the back rim.",
    "{shooter} rattles it out.",
]

FREE_THROW_ROUTINE_TEMPLATES = [
    "{shooter} steps to the line. {attempt} of {total}.",
    "{shooter} at the charity stripe for {total}.",
]

SUBSTITUTION_TEMPLATES = [
    "{player_in} checks in for {player_out}. {team} makes the change.",
    "Substitution: {player_in} replaces {player_out} for {team}.",
    "{player_out} heads to the bench. {player_in} comes in for {team}.",
    "{team} goes to the bench. {player_in} in, {player_out} out.",
    "Fresh legs: {player_in} in for {player_out}.",
]

SUBSTITUTION_REASON_FATIGUE = [
    "{player_out} has been out there a while. Gets a breather.",
    "{player_out} is gassed. {player_in} comes in to spell him.",
    "Rest for {player_out}. He's played {minutes} minutes.",
]

SUBSTITUTION_REASON_FOULS = [
    "{player_out} picks up his {fouls}th foul. Has to sit.",
    "Foul trouble for {player_out}. Can't afford another one.",
    "{player_out} to the bench with {fouls} fouls.",
]

TIMEOUT_TEMPLATES = [
    "Timeout called by {team}. They have {remaining} remaining.",
    "{team} takes a timeout to stop the bleeding.",
    "{team} wants to regroup. Timeout.",
    "Full timeout, {team}. {remaining} left.",
    "{team} calls for time.",
]

TIMEOUT_CONTEXT_RUN = [
    "{opponent} on a {run_points}-{run_against} run. {team} calls timeout.",
    "{team} has to stop the momentum. Timeout.",
    "Smart timeout by {team} to stop {opponent}'s run.",
]

TIMEOUT_CONTEXT_CLUTCH = [
    "Strategic timeout by {team}. Need to draw something up here.",
    "{team} uses a timeout to set up the play. {time} left.",
    "Late-game timeout. {team} needs a bucket.",
]

BETWEEN_QUARTER_TEMPLATES = [
    "End of the {quarter}. {home_team} {home_score}, {away_team} {away_score}.",
    "That's the {quarter}! {home_team} leads {home_score}-{away_score}."
    if True
    else "",
    "Buzzer sounds to end the {quarter}.",
]

HALFTIME_TEMPLATES = [
    "That's halftime! {home_team} {home_score}, {away_team} {away_score}.",
    "We've reached the half. {home_team} leads {home_score}-{away_score}.",
    "Halftime score: {home_team} {home_score}, {away_team} {away_score}.",
]
