"""Tests for energy system."""

from __future__ import annotations

import pytest

from hoops_sim.physical.energy import EnergyManager, EnergyState


class TestEnergyState:
    def test_default(self):
        e = EnergyState()
        assert e.pct == 1.0
        assert e.fatigue_tier() == 0

    def test_drain(self):
        e = EnergyState(current=100.0, max_energy=100.0)
        e.drain(30.0)
        assert e.current == pytest.approx(70.0)
        assert e.pct == pytest.approx(0.7)

    def test_recover(self):
        e = EnergyState(current=50.0, max_energy=100.0)
        e.recover(20.0)
        assert e.current == pytest.approx(70.0)

    def test_cant_exceed_max(self):
        e = EnergyState(current=95.0, max_energy=100.0)
        e.recover(50.0)
        assert e.current == 100.0

    def test_cant_go_below_zero(self):
        e = EnergyState(current=5.0, max_energy=100.0)
        e.drain(50.0)
        assert e.current == 0.0

    def test_fatigue_tiers(self):
        e = EnergyState(max_energy=100.0)
        e.current = 90.0
        assert e.fatigue_tier() == 0
        e.current = 50.0
        assert e.fatigue_tier() == 2
        e.current = 10.0
        assert e.fatigue_tier() == 4

    def test_fatigue_penalty(self):
        e = EnergyState(max_energy=100.0)
        e.current = 100.0
        assert e.fatigue_penalty() == 1.0
        e.current = 10.0
        assert e.fatigue_penalty() < 0.85


class TestEnergyManager:
    def test_init_player(self):
        mgr = EnergyManager()
        mgr.init_player(1, stamina=80)
        state = mgr.get(1)
        assert state.max_energy > 100

    def test_drain_action(self):
        mgr = EnergyManager()
        mgr.init_player(1, stamina=70)
        initial = mgr.get(1).current
        mgr.drain_action(1, 5.0)
        assert mgr.get(1).current < initial

    def test_recover_bench(self):
        mgr = EnergyManager()
        mgr.init_player(1, stamina=70)
        mgr.drain_action(1, 30.0)
        before = mgr.get(1).current
        mgr.recover_bench(1, ticks=10)
        assert mgr.get(1).current > before

    def test_recover_timeout(self):
        mgr = EnergyManager()
        mgr.init_player(1, stamina=70)
        mgr.drain_action(1, 30.0)
        before = mgr.get(1).current
        mgr.recover_timeout([1])
        assert mgr.get(1).current > before
