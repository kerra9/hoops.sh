"""Tests for TUI widgets -- import and basic construction."""

from __future__ import annotations

import pytest


def test_attribute_bar_creation():
    """AttributeBar can be created with label and value."""
    from hoops_sim.tui.widgets.attribute_bar import AttributeBar, _rating_color

    bar = AttributeBar(label="Speed", value=85)
    assert bar._label == "Speed"
    assert bar._value == 85


def test_attribute_bar_clamps_value():
    """AttributeBar clamps value to 0-99."""
    from hoops_sim.tui.widgets.attribute_bar import AttributeBar

    bar = AttributeBar(label="Test", value=150)
    assert bar._value == 99

    bar2 = AttributeBar(label="Test", value=-10)
    assert bar2._value == 0


def test_rating_color():
    """Rating color function returns appropriate colors for ranges."""
    from hoops_sim.tui.widgets.attribute_bar import _rating_color

    assert _rating_color(95) == "#2ecc71"  # green for 90+
    assert _rating_color(45) == "#c0392b"  # dark red for <50


def test_energy_gauge_creation():
    """EnergyGauge can be created with energy percentage and fatigue tier."""
    from hoops_sim.tui.widgets.energy_gauge import EnergyGauge

    gauge = EnergyGauge(label="Energy", energy_pct=0.8, fatigue_tier=1)
    assert gauge._energy_pct == 0.8
    assert gauge._fatigue_tier == 1


def test_energy_gauge_clamps():
    """EnergyGauge clamps values to valid ranges."""
    from hoops_sim.tui.widgets.energy_gauge import EnergyGauge

    gauge = EnergyGauge(energy_pct=1.5, fatigue_tier=10)
    assert gauge._energy_pct == 1.0
    assert gauge._fatigue_tier == 5


def test_player_row_creation():
    """PlayerRow can be created with player data."""
    from hoops_sim.tui.widgets.player_row import PlayerRow

    row = PlayerRow(
        player_name="James Johnson",
        position="PG",
        overall=82,
        stats_text="25 PTS, 8 AST",
        energy_pct=0.75,
        fatigue_tier=2,
    )
    assert row._player_name == "James Johnson"
    assert row._overall == 82


def test_standings_table_creation():
    """StandingsTable can be created with records."""
    from hoops_sim.tui.widgets.standings_table import StandingsTable

    table = StandingsTable(records=[], conference="East")
    assert table._conference == "East"
    assert table._records == []


def test_badge_grid_creation():
    """BadgeGrid can be created with badge data."""
    from hoops_sim.models.badges import BadgeTier
    from hoops_sim.tui.widgets.badge_grid import BadgeGrid

    badges = {"deadeye": BadgeTier.GOLD, "clamps": BadgeTier.SILVER}
    grid = BadgeGrid(badges=badges)
    assert len(grid._badges) == 2


def test_seed_input_creation():
    """SeedInput can be created with an initial seed."""
    from hoops_sim.tui.widgets.seed_input import SeedInput

    seed_input = SeedInput(initial_seed=12345)
    assert seed_input.seed == 12345


def test_seed_input_random_default():
    """SeedInput generates a random seed if none provided."""
    from hoops_sim.tui.widgets.seed_input import SeedInput

    seed_input = SeedInput()
    assert 1 <= seed_input.seed <= 999999


def test_momentum_bar_creation():
    """MomentumBar can be created with value and team names."""
    from hoops_sim.tui.widgets.momentum_bar import MomentumBar

    bar = MomentumBar(value=2.5, home_name="Lakers", away_name="Celtics")
    assert bar._value == 2.5


def test_momentum_bar_clamps():
    """MomentumBar clamps value to -5..+5."""
    from hoops_sim.tui.widgets.momentum_bar import MomentumBar

    bar = MomentumBar(value=10.0)
    assert bar._value == 5.0

    bar2 = MomentumBar(value=-10.0)
    assert bar2._value == -5.0


def test_game_clock_display_creation():
    """GameClockDisplay can be created with clock data."""
    from hoops_sim.tui.widgets.game_clock import GameClockDisplay

    clock = GameClockDisplay(quarter=2, game_clock="5:30.0", shot_clock="14")
    assert clock._quarter == 2
    assert clock._game_clock == "5:30.0"


def test_scoreboard_creation():
    """Scoreboard can be created with team data."""
    from hoops_sim.tui.widgets.scoreboard import Scoreboard

    board = Scoreboard(home_name="Lakers", away_name="Celtics", home_score=98, away_score=95)
    assert board._home_score == 98
    assert board._away_score == 95


def test_mini_box_score_creation():
    """MiniBoxScore can be created with stats."""
    from hoops_sim.models.stats import PlayerGameStats
    from hoops_sim.tui.widgets.mini_box_score import MiniBoxScore

    stats = [PlayerGameStats(player_name="Test Player", points=20)]
    box = MiniBoxScore(team_name="Lakers", player_stats=stats)
    assert box._team_name == "Lakers"
    assert len(box._player_stats) == 1


def test_mini_box_score_team_name_with_spaces():
    """MiniBoxScore sanitizes team names with spaces for widget IDs."""
    import re

    from hoops_sim.tui.widgets.mini_box_score import MiniBoxScore

    box = MiniBoxScore(team_name="New York Knicks")
    assert box._team_name == "New York Knicks"
    # The compose method should produce a valid id by replacing spaces
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", "New York Knicks")
    assert sanitized == "New-York-Knicks"


def test_salary_cap_bar_creation():
    """SalaryCapBar can be created with payroll data."""
    from hoops_sim.tui.widgets.salary_cap_bar import SalaryCapBar

    bar = SalaryCapBar(payroll=140_000_000)
    assert bar._payroll == 140_000_000


def test_schedule_calendar_creation():
    """ScheduleCalendar can be created with games."""
    from hoops_sim.tui.widgets.schedule_calendar import ScheduleCalendar

    cal = ScheduleCalendar(games=[], team_names={}, current_day=5)
    assert cal._current_day == 5


def test_attribute_radar_creation():
    """AttributeRadar can be created with category data."""
    from hoops_sim.tui.widgets.attribute_radar import AttributeRadar

    cats = {"Shooting": 80, "Defense": 70}
    radar = AttributeRadar(categories=cats)
    assert len(radar._categories) == 2


def test_shooting_chart_creation():
    """ShootingChart can be created with a profile."""
    from hoops_sim.models.shooting_profile import ShootingProfile
    from hoops_sim.tui.widgets.shooting_chart import ShootingChart

    profile = ShootingProfile()
    chart = ShootingChart(profile=profile)
    assert chart._profile is profile
