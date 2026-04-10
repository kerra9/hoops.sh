"""Tests for TUI screens -- import verification and basic construction."""

from __future__ import annotations

import pytest


def test_main_menu_screen_import():
    """MainMenuScreen can be imported."""
    from hoops_sim.tui.screens.main_menu import MainMenuScreen

    screen = MainMenuScreen()
    assert screen is not None


def test_season_setup_screen_import():
    """SeasonSetupScreen can be imported."""
    from hoops_sim.tui.screens.season_setup import SeasonSetupScreen

    screen = SeasonSetupScreen()
    assert screen is not None


def test_settings_screen_import():
    """SettingsScreen can be imported."""
    from hoops_sim.tui.screens.settings import SettingsScreen

    screen = SettingsScreen()
    assert screen is not None


def test_standings_screen_import():
    """StandingsScreen can be imported."""
    from hoops_sim.season.standings import Standings
    from hoops_sim.tui.screens.standings import StandingsScreen

    standings = Standings()
    screen = StandingsScreen(standings=standings)
    assert screen is not None


def test_box_score_screen_import():
    """BoxScoreScreen can be imported."""
    from hoops_sim.models.stats import TeamGameStats
    from hoops_sim.tui.screens.box_score import BoxScoreScreen

    home = TeamGameStats()
    away = TeamGameStats()
    screen = BoxScoreScreen(home_stats=home, away_stats=away)
    assert screen is not None


def test_post_game_screen_import():
    """PostGameScreen can be imported."""
    from hoops_sim.models.stats import TeamGameStats
    from hoops_sim.tui.screens.post_game import PostGameScreen

    home = TeamGameStats()
    away = TeamGameStats()
    screen = PostGameScreen(home_stats=home, away_stats=away)
    assert screen is not None


def test_sim_results_screen_import():
    """SimResultsScreen can be imported."""
    from hoops_sim.tui.screens.sim_results import SimResultsScreen

    screen = SimResultsScreen(games=[], team_names={}, day=1)
    assert screen is not None


def test_league_hub_screen_import():
    """LeagueHubScreen can be imported with required data."""
    from hoops_sim.models.league import League
    from hoops_sim.models.team import Team
    from hoops_sim.season.schedule import SeasonSchedule
    from hoops_sim.season.standings import Standings
    from hoops_sim.tui.screens.league_hub import LeagueHubScreen

    league = League(teams=[Team(id=1, city="Test", name="Team")])
    schedule = SeasonSchedule()
    standings = Standings()
    standings.add_team(1, "Test Team", "East", "Atlantic")
    screen = LeagueHubScreen(league=league, schedule=schedule, standings=standings)
    assert screen is not None


def test_team_dashboard_screen_import():
    """TeamDashboardScreen can be imported."""
    from hoops_sim.models.league import League
    from hoops_sim.models.team import Team
    from hoops_sim.tui.screens.team_dashboard import TeamDashboardScreen

    team = Team(id=1, city="Test", name="Team")
    league = League(teams=[team])
    screen = TeamDashboardScreen(team=team, league=league)
    assert screen is not None


def test_roster_mgmt_screen_import():
    """RosterManagementScreen can be imported."""
    from hoops_sim.models.team import Team
    from hoops_sim.tui.screens.roster_mgmt import RosterManagementScreen

    team = Team(id=1, city="Test", name="Team")
    screen = RosterManagementScreen(team=team)
    assert screen is not None


def test_player_card_screen_import():
    """PlayerCardScreen can be imported."""
    from hoops_sim.models.player import Player
    from hoops_sim.tui.screens.player_card import PlayerCardScreen

    player = Player(first_name="Test", last_name="Player")
    screen = PlayerCardScreen(player=player)
    assert screen is not None


def test_schedule_screen_import():
    """ScheduleScreen can be imported."""
    from hoops_sim.models.league import League
    from hoops_sim.season.schedule import SeasonSchedule
    from hoops_sim.tui.screens.schedule import ScheduleScreen

    schedule = SeasonSchedule()
    league = League()
    screen = ScheduleScreen(schedule=schedule, league=league)
    assert screen is not None


def test_app_import():
    """HoopsApp can be imported."""
    from hoops_sim.tui.app import HoopsApp

    app = HoopsApp()
    assert app is not None
    assert app.TITLE == "hoops.sh"


def test_help_screen_import():
    """HelpScreen can be imported."""
    from hoops_sim.tui.screens.help import HelpScreen

    screen = HelpScreen()
    assert screen is not None


def test_messages_import():
    """Custom messages can be imported."""
    from hoops_sim.tui.messages import (
        SimCourtUpdate,
        SimGameOver,
        SimNarration,
        SimSpeedChanged,
        SimTick,
    )

    tick = SimTick(home_score=10, away_score=5)
    assert tick.home_score == 10
    assert tick.away_score == 5


def test_workers_import():
    """SimulationWorker can be imported."""
    from hoops_sim.tui.workers import SimulationWorker

    assert SimulationWorker is not None


def test_base_compat():
    """Base module re-exports Textual classes."""
    from hoops_sim.tui.base import App, Screen, Widget, strip_markup

    assert App is not None
    assert Screen is not None
    assert Widget is not None
    assert strip_markup("[bold]test[/]") == "test"
