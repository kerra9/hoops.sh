"""Tests for the save/load persistence system."""

import json
import tempfile
from pathlib import Path

from hoops_sim.data.generator import generate_roster
from hoops_sim.models.league import League
from hoops_sim.models.team import Team
from hoops_sim.persistence.save_load import save_game, load_game, list_saves
from hoops_sim.season.standings import Standings
from hoops_sim.utils.rng import SeededRNG


def _make_league() -> League:
    rng = SeededRNG(seed=42)
    teams = []
    for i in range(2):
        roster = generate_roster(SeededRNG(seed=100 + i))
        teams.append(Team(
            id=i + 1,
            city=f"City{i}",
            name=f"Team{i}",
            abbreviation=f"T{i}",
            conference="East",
            division="Atlantic",
            roster=roster,
        ))
    return League(name="TestNBA", season_year=2025, teams=teams)


class TestSaveLoad:
    def test_save_creates_file(self):
        league = _make_league()
        standings = Standings()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_game(league, standings, save_name="test", save_dir=Path(tmpdir))
            assert path.exists()
            assert path.suffix == ".json"

    def test_round_trip(self):
        league = _make_league()
        standings = Standings()
        standings.add_team(1, "City0 Team0", "East", "Atlantic")
        standings.record_game(1, 2, 110, 100, True, True, True)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_game(
                league, standings, save_name="rt",
                current_day=10, seed=99, user_team_id=1,
                save_dir=Path(tmpdir),
            )
            loaded_league, loaded_standings, meta = load_game(path)

        assert loaded_league.name == "TestNBA"
        assert len(loaded_league.teams) == 2
        assert loaded_league.teams[0].roster_size() > 0
        assert meta["current_day"] == 10
        assert meta["seed"] == 99

    def test_player_attributes_preserved(self):
        league = _make_league()
        standings = Standings()
        original_player = league.teams[0].roster[0]
        orig_3pt = original_player.attributes.shooting.three_point

        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_game(league, standings, save_dir=Path(tmpdir))
            loaded, _, _ = load_game(path)

        loaded_player = loaded.teams[0].roster[0]
        assert loaded_player.attributes.shooting.three_point == orig_3pt
        assert loaded_player.full_name == original_player.full_name

    def test_list_saves(self):
        league = _make_league()
        standings = Standings()
        with tempfile.TemporaryDirectory() as tmpdir:
            save_game(league, standings, save_name="save1", save_dir=Path(tmpdir))
            save_game(league, standings, save_name="save2", save_dir=Path(tmpdir))
            saves = list_saves(Path(tmpdir))
            assert len(saves) == 2
