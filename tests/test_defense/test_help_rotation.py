"""Tests for help defense and rotation chain logic."""

from __future__ import annotations

import pytest

from hoops_sim.defense.help_rotation import (
    HelpRotationResult,
    evaluate_help_rotation,
)
from hoops_sim.physics.vec import Vec2


class TestHelpRotation:
    def test_no_help_needed_when_defender_not_beaten(self):
        result = evaluate_help_rotation(
            ball_handler_pos=Vec2(60.0, 25.0),
            ball_handler_defender_pos=Vec2(62.0, 25.0),  # Close and in front
            basket_pos=Vec2(88.75, 25.0),
            other_defenders=[
                (2, Vec2(75.0, 15.0), Vec2(70.0, 12.0), 70),
                (3, Vec2(75.0, 35.0), Vec2(70.0, 38.0), 65),
                (4, Vec2(80.0, 25.0), Vec2(82.0, 25.0), 75),
            ],
            offense_positions=[
                (12, Vec2(70.0, 12.0)),
                (13, Vec2(70.0, 38.0)),
                (14, Vec2(82.0, 25.0)),
            ],
        )
        assert result.drive_stopped is True
        assert result.rotation_quality == 1.0

    def test_help_needed_when_defender_beaten(self):
        result = evaluate_help_rotation(
            ball_handler_pos=Vec2(78.0, 25.0),  # Close to basket
            ball_handler_defender_pos=Vec2(60.0, 25.0),  # Way behind
            basket_pos=Vec2(88.75, 25.0),
            other_defenders=[
                (2, Vec2(75.0, 15.0), Vec2(70.0, 12.0), 70),
                (3, Vec2(80.0, 25.0), Vec2(70.0, 38.0), 75),
                (4, Vec2(82.0, 30.0), Vec2(82.0, 30.0), 60),
            ],
            offense_positions=[
                (12, Vec2(70.0, 12.0)),
                (13, Vec2(70.0, 38.0)),
                (14, Vec2(82.0, 30.0)),
            ],
        )
        assert result.drive_stopped is True
        assert result.help_defender_id is not None
        assert result.open_player_id is not None  # Someone got left open

    def test_kick_out_available(self):
        result = evaluate_help_rotation(
            ball_handler_pos=Vec2(80.0, 25.0),
            ball_handler_defender_pos=Vec2(58.0, 25.0),
            basket_pos=Vec2(88.75, 25.0),
            other_defenders=[
                (2, Vec2(75.0, 15.0), Vec2(65.0, 8.0), 70),
                (3, Vec2(82.0, 25.0), Vec2(65.0, 42.0), 75),
            ],
            offense_positions=[
                (12, Vec2(65.0, 8.0)),  # Perimeter player
                (13, Vec2(65.0, 42.0)),  # Perimeter player
            ],
        )
        # Help defender leaves a perimeter player open
        assert result.help_defender_id is not None
