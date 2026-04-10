"""Defensive action templates -- closeouts, help, switches, blocks, steals."""

from __future__ import annotations

CLOSEOUT_TEMPLATES = [
    "{defender} closes out hard on {shooter}!",
    "{defender} gets out to contest!",
    "Good closeout by {defender}!",
    "{defender} sprints out to challenge the shot!",
    "{defender} recovers and gets a hand up!",
]

HELP_ROTATION_TEMPLATES = [
    "{helper} rotates over from the weak side!",
    "{helper} slides into the lane to cut off the drive!",
    "Here comes the help from {helper}!",
    "{helper} leaves his man to help on the drive!",
    "The defense rotates! {helper} picks up the driver.",
]

SWITCH_DEFENSE_TEMPLATES = [
    "They switch everything on defense.",
    "Switch! {defender} now picks up {attacker}.",
    "The defense switches on that action.",
]

BLOCK_TEMPLATES = [
    "{blocker} SWATS {shooter}'s shot away! What a block!",
    "{blocker} comes from the weak side... REJECTED!",
    "{shooter} tries to finish... BLOCKED by {blocker}!",
    "Get that out of here! {blocker} with the emphatic block!",
    "{blocker} pins it against the backboard! Incredible timing!",
    "{blocker} with the chase-down block!",
    "{blocker} says NO! Huge block!",
    "REJECTED by {blocker}! {shooter} had no chance!",
]

STEAL_TEMPLATES = [
    "{defender} reads the pass perfectly... INTERCEPTED!",
    "{defender} jumps the passing lane! Steal!",
    "{defender} pokes it away! Quick hands!",
    "Turnover! {defender} picks {handler}'s pocket!",
    "{defender} with the anticipation... STEAL!",
    "{defender} rips the ball away! Great defense!",
    "{defender} times it perfectly... stolen!",
]

GOOD_DEFENSE_TEMPLATES = [
    "Great defense by {defender} on that possession.",
    "{defender} makes it tough on the offensive player.",
    "Tough defense forces the difficult shot.",
    "{defender} stays in front the entire possession.",
]

SHOT_CLOCK_PRESSURE_TEMPLATES = [
    "Shot clock winding down... {team} scrambling.",
    "Under 5 on the shot clock! {team} needs to get something up.",
    "Shot clock at {seconds}! Desperation time!",
]
