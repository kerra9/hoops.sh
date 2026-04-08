"""Shared test fixtures."""

from __future__ import annotations

import pytest

from hoops_sim.utils.rng import RNGManager, SeededRNG


@pytest.fixture
def rng() -> SeededRNG:
    """A deterministic RNG for tests."""
    return SeededRNG(seed=42)


@pytest.fixture
def rng_manager() -> RNGManager:
    """A deterministic RNG manager for tests."""
    return RNGManager(master_seed=42)
