"""Tests for game clock and shot clock."""

from __future__ import annotations

import pytest

from hoops_sim.engine.clock import GameClock
from hoops_sim.utils.constants import QUARTER_LENGTH_MINUTES, SHOT_CLOCK_SECONDS


class TestGameClock:
    def test_initial_state(self):
        clock = GameClock()
        assert clock.quarter == 1
        assert clock.game_clock == QUARTER_LENGTH_MINUTES * 60.0
        assert clock.shot_clock == SHOT_CLOCK_SECONDS
        assert not clock.is_running

    def test_tick_when_stopped(self):
        clock = GameClock()
        initial = clock.game_clock
        clock.tick(0.1)
        assert clock.game_clock == initial  # Didn't change

    def test_tick_when_running(self):
        clock = GameClock()
        clock.start()
        initial = clock.game_clock
        clock.tick(0.1)
        assert clock.game_clock == pytest.approx(initial - 0.1)
        assert clock.shot_clock == pytest.approx(SHOT_CLOCK_SECONDS - 0.1)

    def test_start_stop(self):
        clock = GameClock()
        clock.start()
        assert clock.is_running
        clock.stop()
        assert not clock.is_running

    def test_display(self):
        clock = GameClock()
        assert "12:" in clock.display

    def test_shot_clock_display(self):
        clock = GameClock()
        assert clock.shot_clock_display == "24"
        clock.shot_clock = 5.3
        assert clock.shot_clock_display == "5.3"

    def test_reset_shot_clock_full(self):
        clock = GameClock()
        clock.shot_clock = 5.0
        clock.reset_shot_clock(full=True)
        assert clock.shot_clock == SHOT_CLOCK_SECONDS

    def test_reset_shot_clock_offensive_rebound(self):
        clock = GameClock()
        clock.shot_clock = 5.0
        clock.reset_shot_clock(full=False)
        assert clock.shot_clock == 14.0

    def test_shot_clock_cant_exceed_game_clock(self):
        clock = GameClock()
        clock.game_clock = 10.0
        clock.reset_shot_clock(full=True)
        assert clock.shot_clock == 10.0

    def test_shot_clock_violation(self):
        clock = GameClock()
        clock.start()
        clock.shot_clock = 0.0
        assert clock.is_shot_clock_violation()

    def test_quarter_over(self):
        clock = GameClock()
        clock.game_clock = 0.0
        assert clock.is_quarter_over()

    def test_start_quarter(self):
        clock = GameClock()
        clock.start_quarter(2)
        assert clock.quarter == 2
        assert clock.game_clock == QUARTER_LENGTH_MINUTES * 60.0
        assert not clock.is_overtime

    def test_start_overtime(self):
        clock = GameClock()
        clock.start_quarter(5)
        assert clock.quarter == 5
        assert clock.game_clock == 5 * 60.0  # 5 minutes
        assert clock.is_overtime

    def test_clutch_time(self):
        clock = GameClock()
        clock.start_quarter(4)
        clock.game_clock = 90.0  # 1:30 left in 4th
        assert clock.is_clutch_time()

        clock.game_clock = 300.0  # 5:00 left in 4th
        assert not clock.is_clutch_time()

    def test_last_two_minutes(self):
        clock = GameClock()
        clock.game_clock = 100.0
        assert clock.is_last_two_minutes()
        clock.game_clock = 200.0
        assert not clock.is_last_two_minutes()

    def test_clock_never_negative(self):
        clock = GameClock()
        clock.start()
        clock.game_clock = 0.05
        clock.shot_clock = 0.05
        clock.tick(0.1)
        assert clock.game_clock >= 0.0
        assert clock.shot_clock >= 0.0
