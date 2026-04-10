"""Tests for the per-player micro-action state machine."""

from __future__ import annotations

import pytest

from hoops_sim.engine.action_fsm import (
    ActionStateMachine,
    BallHandlerState,
    DefenderState,
    MovementIntent,
    OffBallOffenseState,
    PossessionEvent,
    PossessionEventType,
    INTERRUPTIBLE_STATES,
    ACTION_DURATIONS,
)
from hoops_sim.physics.vec import Vec2


class TestActionStateMachine:
    def test_default_state(self):
        fsm = ActionStateMachine()
        assert fsm.current_state == OffBallOffenseState.STANDING
        assert fsm.ticks_remaining == 0
        assert fsm.interruptible is True
        assert fsm.is_complete is True

    def test_transition_to(self):
        fsm = ActionStateMachine()
        target = Vec2(50.0, 25.0)
        fsm.transition_to(
            BallHandlerState.DRIVING,
            ticks=10,
            target=target,
            intent=MovementIntent.SPRINT,
        )
        assert fsm.current_state == BallHandlerState.DRIVING
        assert fsm.ticks_remaining == 10
        assert fsm.movement_target == target
        assert fsm.movement_intent == MovementIntent.SPRINT
        assert fsm.interruptible is False  # DRIVING is not interruptible

    def test_tick_decrements(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.PASSING, ticks=5)
        assert fsm.ticks_remaining == 5
        completed = fsm.tick()
        assert fsm.ticks_remaining == 4
        assert completed is False

    def test_tick_completes(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.PASSING, ticks=1)
        completed = fsm.tick()
        assert completed is True
        assert fsm.is_complete is True

    def test_interruptible_states(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.DRIBBLING_IN_PLACE, ticks=10)
        assert fsm.interruptible is True
        assert fsm.can_interrupt is True

    def test_non_interruptible_states(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.DRIVING, ticks=10)
        assert fsm.interruptible is False
        assert fsm.can_interrupt is False

    def test_can_interrupt_when_complete(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.DRIVING, ticks=1)
        fsm.tick()
        assert fsm.can_interrupt is True  # Complete overrides non-interruptible

    def test_combo_tracking(self):
        fsm = ActionStateMachine()
        assert fsm.combo_count == 0
        fsm.increment_combo(True)
        assert fsm.combo_count == 1
        fsm.increment_combo(True)
        assert fsm.combo_count == 2
        fsm.increment_combo(False)  # Failed move resets
        assert fsm.combo_count == 0

    def test_reset_combo(self):
        fsm = ActionStateMachine()
        fsm.increment_combo(True)
        fsm.increment_combo(True)
        fsm.reset_combo()
        assert fsm.combo_count == 0
        assert fsm.last_dribble_success is False

    def test_defender_separation(self):
        fsm = ActionStateMachine()
        assert fsm.defender_separation == 3.0
        fsm.defender_separation += 2.5
        assert fsm.defender_separation == 5.5

    def test_is_ball_handler_state(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.DRIVING, ticks=5)
        assert fsm.is_ball_handler_state is True
        assert fsm.is_offense_state is True
        assert fsm.is_defense_state is False

    def test_is_defense_state(self):
        fsm = ActionStateMachine()
        fsm.transition_to(DefenderState.GUARDING_ON_BALL, ticks=5)
        assert fsm.is_defense_state is True
        assert fsm.is_offense_state is False

    def test_is_offense_state(self):
        fsm = ActionStateMachine()
        fsm.transition_to(OffBallOffenseState.CUTTING, ticks=5)
        assert fsm.is_offense_state is True
        assert fsm.is_ball_handler_state is False

    def test_context_passed_through(self):
        fsm = ActionStateMachine()
        fsm.transition_to(
            BallHandlerState.EXECUTING_DRIBBLE_MOVE,
            ticks=5,
            context={"move_type": "crossover"},
        )
        assert fsm.context["move_type"] == "crossover"

    def test_context_cleared_on_transition(self):
        fsm = ActionStateMachine()
        fsm.transition_to(
            BallHandlerState.DRIVING, ticks=5, context={"old": True},
        )
        fsm.transition_to(BallHandlerState.PASSING, ticks=3)
        assert fsm.context == {}

    def test_ticks_minimum_one(self):
        fsm = ActionStateMachine()
        fsm.transition_to(BallHandlerState.PASSING, ticks=0)
        assert fsm.ticks_remaining == 1  # Minimum 1 tick

    def test_all_durations_defined(self):
        """Every micro-action should have a duration range."""
        all_states = (
            list(BallHandlerState)
            + list(OffBallOffenseState)
            + list(DefenderState)
        )
        for state in all_states:
            assert state in ACTION_DURATIONS, f"Missing duration for {state}"
            min_t, max_t = ACTION_DURATIONS[state]
            assert min_t > 0
            assert max_t >= min_t


class TestPossessionEvent:
    def test_create_event(self):
        ev = PossessionEvent(
            event_type=PossessionEventType.MADE_BASKET,
            player_id=42,
            description="Splash!",
        )
        assert ev.event_type == PossessionEventType.MADE_BASKET
        assert ev.player_id == 42
        assert ev.description == "Splash!"

    def test_event_with_data(self):
        ev = PossessionEvent(
            event_type=PossessionEventType.DRIBBLE_MOVE_SUCCESS,
            player_id=1,
            data={"move_type": "crossover", "separation": 2.5},
        )
        assert ev.data["move_type"] == "crossover"
        assert ev.data["separation"] == 2.5
