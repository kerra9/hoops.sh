"""Context suffix templates -- stats, streaks, milestones, crowd."""

from __future__ import annotations

# Player scoring milestone
MILESTONE_TEMPLATES = [
    "That gives {player} {points} points tonight!",
    "That's {points} for {player}!",
    "{player} now has {points} on the night.",
    "{player} up to {points} points!",
]

# Shooting line
SHOOTING_LINE_TEMPLATES = [
    "He's {made}-for-{attempted} from the field.",
    "{player} is {made}-of-{attempted} shooting tonight.",
    "That's {made} of {attempted} for {player}.",
]

# Three-point shooting
THREE_POINT_LINE_TEMPLATES = [
    "He's {made}-for-{attempted} from deep tonight.",
    "{player} is {made}-of-{attempted} from three.",
    "That's his {ordinal} triple of the night.",
]

# Hot streak
HOT_STREAK_TEMPLATES = [
    "He can't miss! {count} in a row!",
    "{player} is absolutely on fire right now!",
    "He's in the zone! {count} straight makes!",
    "{player} is feeling it! {count} consecutive buckets!",
]

# Cold streak
COLD_STREAK_TEMPLATES = [
    "He's struggling tonight. {count} straight misses.",
    "{player} can't buy a bucket right now.",
    "Cold shooting for {player}. {count} misses in a row.",
]

# Scoring run
SCORING_RUN_TEMPLATES = [
    "That's a {points}-{against} run for {team}!",
    "{team} on a {points}-point run!",
    "{points} unanswered for {team}!",
    "{team} has scored {points} of the last {total} points!",
]

# Scoring drought
DROUGHT_TEMPLATES = [
    "{team} hasn't scored in {time}.",
    "Scoreless drought for {team}. {time} without a bucket.",
    "{team} going cold. No points in {time}.",
]

# Assist context
ASSIST_TEMPLATES = [
    "That's {player}'s {ordinal} assist tonight.",
    "{player} up to {count} assists.",
    "{player} doing it all -- {count} dimes tonight.",
]

# Crowd reaction
CROWD_REACTION_BIG_PLAY = [
    "The crowd goes wild!",
    "Listen to this crowd!",
    "The building is ROCKING!",
    "The fans are on their feet!",
]

CROWD_REACTION_HOME_RUN = [
    "The home crowd is loving this!",
    "The energy in this building right now!",
    "The roof is about to come off!",
]

CROWD_REACTION_AWAY_SILENCED = [
    "That quiets the home crowd.",
    "Silence in the arena.",
    "The visitors take the energy out of the building.",
]

# Lead change / tie
LEAD_CHANGE_TEMPLATES = [
    "{team} takes the lead!",
    "We've got a new leader! {team} in front by {lead}!",
    "{team} goes ahead for the first time since the {quarter}!",
]

TIE_GAME_TEMPLATES = [
    "We're all tied up!",
    "Back to even! What a game!",
    "Tied up again!",
]

# Game situation
CLUTCH_TEMPLATES = [
    "Clutch! {player} delivers when it matters most!",
    "Ice in his veins! {player} in crunch time!",
    "Big-time shot by {player}!",
]

GARBAGE_TIME_TEMPLATES = [
    "The benches are in now.",
    "Both coaches going deep into their bench.",
]


def ordinal(n: int) -> str:
    """Convert integer to ordinal string (1st, 2nd, 3rd, etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
