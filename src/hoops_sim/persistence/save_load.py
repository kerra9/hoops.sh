"""Save/Load system: serialize and deserialize entire league state.

Supports saving to JSON files and loading back. Auto-save can be
triggered after each simulated day.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any

from hoops_sim.models.attributes import (
    AthleticAttributes,
    DefensiveAttributes,
    FinishingAttributes,
    MentalAttributes,
    PlayerAttributes,
    PlaymakingAttributes,
    ReboundingAttributes,
    ShootingAttributes,
)
from hoops_sim.models.badges import BadgeTier, PlayerBadges
from hoops_sim.models.body import PlayerBody
from hoops_sim.models.league import League
from hoops_sim.models.lifestyle import PlayerLifestyle
from hoops_sim.models.personality import PlayerPersonality
from hoops_sim.models.player import Player, Position
from hoops_sim.models.shooting_profile import ShootingProfile
from hoops_sim.models.team import Team
from hoops_sim.models.tendencies import PlayerTendencies
from hoops_sim.season.standings import Standings, TeamRecord


DEFAULT_SAVE_DIR = Path.home() / ".hoops_sim" / "saves"


def _serialize_player(player: Player) -> dict[str, Any]:
    """Serialize a Player to a JSON-compatible dict."""
    return {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "age": player.age,
        "position": player.position.value,
        "secondary_position": player.secondary_position.value if player.secondary_position else None,
        "jersey_number": player.jersey_number,
        "years_pro": player.years_pro,
        "attributes": _serialize_attributes(player.attributes),
        "tendencies": asdict(player.tendencies),
        "badges": {k: int(v) for k, v in player.badges.badges.items()},
        "shooting_profile": {str(int(k)): v for k, v in player.shooting_profile.zone_modifiers.items()},
    }


def _serialize_attributes(attrs: PlayerAttributes) -> dict[str, dict[str, int]]:
    """Serialize PlayerAttributes."""
    result: dict[str, dict[str, int]] = {}
    for cat_field in fields(attrs):
        category = getattr(attrs, cat_field.name)
        cat_dict: dict[str, int] = {}
        for attr_field in fields(category):
            cat_dict[attr_field.name] = getattr(category, attr_field.name)
        result[cat_field.name] = cat_dict
    return result


def _deserialize_player(data: dict[str, Any]) -> Player:
    """Deserialize a Player from a dict."""
    attrs_data = data.get("attributes", {})
    attrs = PlayerAttributes(
        shooting=ShootingAttributes(**attrs_data.get("shooting", {})),
        finishing=FinishingAttributes(**attrs_data.get("finishing", {})),
        playmaking=PlaymakingAttributes(**attrs_data.get("playmaking", {})),
        defense=DefensiveAttributes(**attrs_data.get("defense", {})),
        rebounding=ReboundingAttributes(**attrs_data.get("rebounding", {})),
        athleticism=AthleticAttributes(**attrs_data.get("athleticism", {})),
        mental=MentalAttributes(**attrs_data.get("mental", {})),
    )

    tend_data = data.get("tendencies", {})
    tendencies = PlayerTendencies(**tend_data)

    badges_data = data.get("badges", {})
    badges = PlayerBadges(badges={k: BadgeTier(v) for k, v in badges_data.items()})

    from hoops_sim.court.zones import Zone
    sp_data = data.get("shooting_profile", {})
    zone_mods = {}
    for k, v in sp_data.items():
        try:
            zone_mods[Zone(int(k))] = v
        except (ValueError, KeyError):
            pass
    profile = ShootingProfile(zone_modifiers=zone_mods)

    sec_pos = None
    if data.get("secondary_position"):
        sec_pos = Position(data["secondary_position"])

    return Player(
        id=data.get("id", 0),
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        age=data.get("age", 25),
        position=Position(data.get("position", "SF")),
        secondary_position=sec_pos,
        jersey_number=data.get("jersey_number", 0),
        years_pro=data.get("years_pro", 0),
        attributes=attrs,
        tendencies=tendencies,
        badges=badges,
        shooting_profile=profile,
    )


def _serialize_team(team: Team) -> dict[str, Any]:
    """Serialize a Team."""
    return {
        "id": team.id,
        "city": team.city,
        "name": team.name,
        "abbreviation": team.abbreviation,
        "conference": team.conference,
        "division": team.division,
        "roster": [_serialize_player(p) for p in team.roster],
    }


def _deserialize_team(data: dict[str, Any]) -> Team:
    """Deserialize a Team."""
    roster = [_deserialize_player(p) for p in data.get("roster", [])]
    return Team(
        id=data.get("id", 0),
        city=data.get("city", ""),
        name=data.get("name", ""),
        abbreviation=data.get("abbreviation", ""),
        conference=data.get("conference", ""),
        division=data.get("division", ""),
        roster=roster,
    )


def _serialize_standings(standings: Standings) -> dict[str, Any]:
    """Serialize standings."""
    records = {}
    for tid, rec in standings.records.items():
        records[str(tid)] = {
            "team_id": rec.team_id,
            "team_name": rec.team_name,
            "conference": rec.conference,
            "division": rec.division,
            "wins": rec.wins,
            "losses": rec.losses,
            "home_wins": rec.home_wins,
            "home_losses": rec.home_losses,
            "away_wins": rec.away_wins,
            "away_losses": rec.away_losses,
            "conference_wins": rec.conference_wins,
            "conference_losses": rec.conference_losses,
            "division_wins": rec.division_wins,
            "division_losses": rec.division_losses,
            "streak": rec.streak,
            "last_10_wins": rec.last_10_wins,
            "last_10_losses": rec.last_10_losses,
        }
    return records


def _deserialize_standings(data: dict[str, Any]) -> Standings:
    """Deserialize standings."""
    standings = Standings()
    for tid_str, rec_data in data.items():
        rec = TeamRecord(
            team_id=rec_data["team_id"],
            team_name=rec_data.get("team_name", ""),
            conference=rec_data.get("conference", ""),
            division=rec_data.get("division", ""),
            wins=rec_data.get("wins", 0),
            losses=rec_data.get("losses", 0),
            home_wins=rec_data.get("home_wins", 0),
            home_losses=rec_data.get("home_losses", 0),
            away_wins=rec_data.get("away_wins", 0),
            away_losses=rec_data.get("away_losses", 0),
            conference_wins=rec_data.get("conference_wins", 0),
            conference_losses=rec_data.get("conference_losses", 0),
            division_wins=rec_data.get("division_wins", 0),
            division_losses=rec_data.get("division_losses", 0),
            streak=rec_data.get("streak", 0),
            last_10_wins=rec_data.get("last_10_wins", 0),
            last_10_losses=rec_data.get("last_10_losses", 0),
        )
        standings.records[int(tid_str)] = rec
    return standings


@dataclass
class SaveData:
    """Complete save file data."""

    version: int = 1
    save_name: str = ""
    timestamp: str = ""
    season_year: int = 2025
    current_day: int = 0
    seed: int = 42
    user_team_id: int = 0


def save_game(
    league: League,
    standings: Standings,
    save_name: str = "autosave",
    current_day: int = 0,
    seed: int = 42,
    user_team_id: int = 0,
    save_dir: Path | None = None,
) -> Path:
    """Save the entire league state to a JSON file.

    Args:
        league: The league to save.
        standings: Current standings.
        save_name: Name for the save file.
        current_day: Current simulation day.
        seed: Master RNG seed.
        user_team_id: The user's team ID.
        save_dir: Directory to save in (defaults to ~/.hoops_sim/saves).

    Returns:
        Path to the saved file.
    """
    if save_dir is None:
        save_dir = DEFAULT_SAVE_DIR
    save_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "version": 1,
        "save_name": save_name,
        "timestamp": datetime.now().isoformat(),
        "season_year": league.season_year,
        "current_day": current_day,
        "seed": seed,
        "user_team_id": user_team_id,
        "league": {
            "name": league.name,
            "season_year": league.season_year,
            "teams": [_serialize_team(t) for t in league.teams],
        },
        "standings": _serialize_standings(standings),
    }

    filepath = save_dir / f"{save_name}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath


def load_game(filepath: Path) -> tuple[League, Standings, dict[str, Any]]:
    """Load a saved game from a JSON file.

    Args:
        filepath: Path to the save file.

    Returns:
        Tuple of (League, Standings, metadata dict with save_name, seed, etc.)
    """
    with open(filepath) as f:
        data = json.load(f)

    # Deserialize league
    league_data = data.get("league", {})
    teams = [_deserialize_team(t) for t in league_data.get("teams", [])]
    league = League(
        name=league_data.get("name", "NBA"),
        season_year=league_data.get("season_year", 2025),
        teams=teams,
    )

    # Deserialize standings
    standings = _deserialize_standings(data.get("standings", {}))

    # Metadata
    meta = {
        "save_name": data.get("save_name", ""),
        "timestamp": data.get("timestamp", ""),
        "current_day": data.get("current_day", 0),
        "seed": data.get("seed", 42),
        "user_team_id": data.get("user_team_id", 0),
    }

    return league, standings, meta


def list_saves(save_dir: Path | None = None) -> list[dict[str, Any]]:
    """List all save files with their metadata.

    Returns:
        List of dicts with save_name, timestamp, filepath, etc.
    """
    if save_dir is None:
        save_dir = DEFAULT_SAVE_DIR

    if not save_dir.exists():
        return []

    saves = []
    for f in sorted(save_dir.glob("*.json")):
        try:
            with open(f) as fh:
                data = json.load(fh)
            saves.append({
                "filepath": str(f),
                "save_name": data.get("save_name", f.stem),
                "timestamp": data.get("timestamp", ""),
                "season_year": data.get("season_year", 0),
                "current_day": data.get("current_day", 0),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return saves


def delete_save(filepath: Path) -> bool:
    """Delete a save file."""
    try:
        filepath.unlink()
        return True
    except OSError:
        return False
