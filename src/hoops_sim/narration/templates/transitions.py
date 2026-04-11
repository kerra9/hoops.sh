"""Possession transition templates -- bridge narration between possessions.

Real broadcasts always describe the change of possession: who's bringing
the ball up, whether it's after a made basket, turnover, or rebound.
These templates fill the gap that makes the narration read like a
continuous broadcast instead of isolated events.
"""

from __future__ import annotations

# After a made basket (defending team inbounds)
INBOUND_AFTER_SCORE_TEMPLATES = [
    "{team} bring it up after the made basket.",
    "{team} ball. {handler} brings it up court.",
    "{handler} inbounds for {team}.",
    "Change of possession. {team} with the ball.",
    "{team} take it out at the baseline.",
    "{handler} takes it coast to coast for {team}.",
    "Back the other way. {team} ball.",
    "{handler} walks it up for {team} after the bucket.",
]

# After a turnover
AFTER_TURNOVER_TEMPLATES = [
    "{team} capitalize on the turnover.",
    "Change of possession after the turnover. {team} ball.",
    "{team} with a chance to make them pay.",
    "That's {team} ball after the giveaway.",
    "{handler} pushes it the other way for {team}.",
    "Turnover. {team} looking to take advantage.",
]

# After a defensive rebound
AFTER_REBOUND_TEMPLATES = [
    "{rebounder} outlets to {handler}. {team} on the attack.",
    "{team} with the rebound. Here they come.",
    "Off the miss, {team} ball.",
    "{rebounder} grabs it and pushes ahead.",
    "Rebound {team}. New possession.",
    "{team} come away with the board.",
]

# Periodic scoreboard recap (every 4-5 possessions)
SCOREBOARD_RECAP_TEMPLATES = [
    "Score check: {home_team} {home_score}, {away_team} {away_score} with {clock} left in the {quarter}.",
    "We've got {home_team} {home_score}, {away_team} {away_score}. {clock} remaining in the {quarter}.",
    "{home_team} leading {home_score}-{away_score} with {clock} to go." if True else "",
    "It's {home_team} {home_score}, {away_team} {away_score} here in the {quarter}.",
    "{clock} left. {home_team} {home_score}, {away_team} {away_score}.",
]
