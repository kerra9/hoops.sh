"""Tests for TUI widgets -- import and basic construction."""

from __future__ import annotations

import pytest


def test_attribute_bar_creation():
    """AttributeBar can be created with label and value."""
    from hoops_sim.tui.widgets.attribute_bar import AttributeBar

    bar = AttributeBar(label="Speed", value=85)
    assert bar._label == "Speed"
    assert bar._value == 85


def test_attribute_bar_stores_value():
    """AttributeBar stores the max_value parameter."""
    from hoops_sim.tui.widgets.attribute_bar import AttributeBar

    bar = AttributeBar(label="Test", value=50, max_value=99)
    assert bar._value == 50
    assert bar._max_value == 99


def test_rating_color():
    """Rating color function returns appropriate colors for ranges."""
    from hoops_sim.tui.theme import rating_color

    assert rating_color(95) == "#2ecc71"  # green for 90+
    assert rating_color(45) == "#c0392b"  # dark red for <50


def test_energy_gauge_creation():
    """EnergyGauge can be created with value and label."""
    from hoops_sim.tui.widgets.energy_gauge import EnergyGauge

    gauge = EnergyGauge(value=0.8, label="Energy")
    assert gauge._value == 0.8
    assert gauge._label == "Energy"


def test_energy_gauge_clamps():
    """EnergyGauge clamps values to valid ranges."""
    from hoops_sim.tui.widgets.energy_gauge import EnergyGauge

    gauge = EnergyGauge(value=1.5)
    assert gauge._value == 1.0

    gauge2 = EnergyGauge(value=-0.5)
    assert gauge2._value == 0.0


def test_player_row_creation():
    """PlayerRow can be created with player data."""
    from hoops_sim.tui.widgets.player_row import PlayerRow

    row = PlayerRow(
        name="James Johnson",
        position="PG",
        overall=82,
        energy_pct=0.75,
    )
    assert row._name == "James Johnson"
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
    """SeedInput can be created with an initial value."""
    from hoops_sim.tui.widgets.seed_input import SeedInput

    seed_input = SeedInput(value=12345)
    assert seed_input._value == 12345


def test_seed_input_default():
    """SeedInput has a default value."""
    from hoops_sim.tui.widgets.seed_input import SeedInput

    seed_input = SeedInput()
    assert seed_input._value == 42


def test_momentum_bar_creation():
    """MomentumBar can be created with value and team names."""
    from hoops_sim.tui.widgets.momentum_bar import MomentumBar

    bar = MomentumBar(value=2.5, home_name="Lakers", away_name="Celtics")
    assert bar.value == 2.5


def test_momentum_bar_clamps():
    """MomentumBar clamps value to -5..+5."""
    from hoops_sim.tui.widgets.momentum_bar import MomentumBar

    bar = MomentumBar(value=10.0)
    assert bar.value == 5.0

    bar2 = MomentumBar(value=-10.0)
    assert bar2.value == -5.0


def test_game_clock_creation():
    """GameClock can be created."""
    from hoops_sim.tui.widgets.game_clock import GameClock

    clock = GameClock()
    assert clock.quarter == 1
    assert clock.display == "12:00.0"


def test_scoreboard_creation():
    """Scoreboard (BroadcastScoreboard) can be created with team data."""
    from hoops_sim.tui.widgets.scoreboard import Scoreboard

    board = Scoreboard(home_name="Lakers", away_name="Celtics")
    assert board.home_score == 0
    assert board.away_score == 0


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
    """ScheduleCalendar (WeekCalendarGrid) can be created."""
    from hoops_sim.tui.widgets.schedule_calendar import ScheduleCalendar

    cal = ScheduleCalendar(current_day=5)
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


# ── New widget tests ──────────────────────────────────────────


def test_broadcast_scoreboard_creation():
    """BroadcastScoreboard can be created."""
    from hoops_sim.tui.widgets.broadcast_scoreboard import BroadcastScoreboard

    sb = BroadcastScoreboard(home_name="Lakers", away_name="Celtics")
    assert sb.home_score == 0
    assert sb.away_score == 0


def test_court_map_creation():
    """CourtMap can be created."""
    from hoops_sim.tui.widgets.court_map import CourtMap

    court = CourtMap()
    assert court._offense == []
    assert court._defense == []


def test_context_strip_creation():
    """ContextStrip can be created."""
    from hoops_sim.tui.widgets.context_strip import ContextStrip

    strip = ContextStrip(home_name="Lakers", away_name="Celtics")
    assert strip.momentum == 0.0


def test_court_shooting_chart_creation():
    """CourtShootingChart can be created."""
    from hoops_sim.tui.widgets.court_shooting_chart import CourtShootingChart

    chart = CourtShootingChart()
    assert chart._profile is None

    from hoops_sim.models.shooting_profile import ShootingProfile
    chart2 = CourtShootingChart(profile=ShootingProfile())
    assert chart2._profile is not None


def test_career_sparkline():
    """CareerSparkline can be created with values."""
    from hoops_sim.tui.widgets.career_sparkline import CareerSparkline

    spark = CareerSparkline(values=[1.0, 2.0, 3.0, 4.0, 5.0], label="PPG")
    assert len(spark._values) == 5
    assert spark._label == "PPG"


def test_career_sparkline_empty():
    """CareerSparkline handles empty input."""
    from hoops_sim.tui.widgets.career_sparkline import CareerSparkline

    spark = CareerSparkline()
    assert spark._values == []


def test_final_score_display():
    """FinalScoreDisplay can be created."""
    from hoops_sim.tui.widgets.final_score import FinalScoreDisplay

    display = FinalScoreDisplay(
        home_name="Lakers", away_name="Celtics",
        home_score=102, away_score=98,
    )
    assert display._home_score == 102


def test_game_leaders_panel():
    """GameLeadersPanel can be created."""
    from hoops_sim.tui.widgets.game_leaders import GameLeadersPanel

    panel = GameLeadersPanel(
        leaders=[("PTS", "LeBron", "28"), ("REB", "AD", "12")]
    )
    assert len(panel._leaders) == 2


def test_quarter_scoring_table():
    """QuarterScoringTable can be created."""
    from hoops_sim.tui.widgets.quarter_scoring import QuarterScoringTable

    table = QuarterScoringTable(
        home_name="LAL", away_name="BOS",
        home_quarters=[22, 30, 26, 24],
        away_quarters=[24, 28, 22, 24],
    )
    assert sum(table._home_quarters) == 102


def test_depth_chart_creation():
    """DepthChart can be created."""
    from hoops_sim.tui.widgets.depth_chart import DepthChart

    depth = {"PG": ["Player1"], "SG": ["Player2"]}
    chart = DepthChart(depth=depth)
    assert len(chart._depth) == 2


def test_playoff_picture_strip():
    """PlayoffPictureStrip can be created."""
    from hoops_sim.tui.widgets.playoff_picture import PlayoffPictureStrip

    strip = PlayoffPictureStrip(
        east_teams=["BOS", "MIL", "CLE"],
        west_teams=["LAL", "DEN", "GSW"],
    )
    assert len(strip._east) == 3


def test_theme_rating_color():
    """Theme rating_color returns valid colors."""
    from hoops_sim.tui.theme import rating_color

    assert rating_color(95).startswith("#")
    assert rating_color(50).startswith("#")
    assert rating_color(10).startswith("#")


def test_theme_energy_color():
    """Theme energy_color returns valid colors."""
    from hoops_sim.tui.theme import energy_color

    assert energy_color(0.9).startswith("#")
    assert energy_color(0.5).startswith("#")
    assert energy_color(0.1).startswith("#")


def test_game_controls_creation():
    """GameControls can be created."""
    from hoops_sim.tui.widgets.game_controls import GameControls

    controls = GameControls()
    assert controls.current_delay == 1.0
    assert controls.current_label == "1x"


def test_game_controls_speed_change():
    """GameControls can change speed."""
    from hoops_sim.tui.widgets.game_controls import GameControls

    controls = GameControls(current_index=1)
    label, delay = controls.speed_up()
    assert label == "2x"
    assert delay == 0.5

    label, delay = controls.slow_down()
    assert label == "1x"
    assert delay == 1.0
