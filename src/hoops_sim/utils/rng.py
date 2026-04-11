"""Seeded random number generator with independent streams per subsystem."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class SeededRNG:
    """A seeded RNG wrapper that provides reproducible randomness.

    Each subsystem (physics, AI, injuries, etc.) can have its own independent
    stream so that changes in one subsystem don't affect the sequence of another.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    @property
    def seed(self) -> int | None:
        return self._seed

    def random(self) -> float:
        """Return a random float in [0.0, 1.0)."""
        return self._rng.random()

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Return a random float from a Gaussian distribution."""
        return self._rng.gauss(mu, sigma)

    def uniform(self, a: float, b: float) -> float:
        """Return a random float in [a, b]."""
        return self._rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        """Return a random integer in [a, b] inclusive."""
        return self._rng.randint(a, b)

    def choice(self, seq: Sequence[T]) -> T:
        """Return a random element from a non-empty sequence."""
        return self._rng.choice(seq)

    def shuffle(self, seq: list[T]) -> None:
        """Shuffle a list in place."""
        self._rng.shuffle(seq)

    def choices(
        self, population: Sequence[T], weights: Sequence[float] | None = None, k: int = 1,
    ) -> list[T]:
        """Return k elements chosen from the population with optional weights."""
        return self._rng.choices(population, weights=weights, k=k)

    def fork(self, label: str) -> SeededRNG:
        """Create a child RNG with a deterministic seed derived from this one.

        This ensures that each subsystem gets its own independent stream while
        still being fully reproducible from the parent seed. The label is mixed
        into the seed so that different subsystems get distinct streams even if
        forked at the same parent state.
        """
        base_seed = self._rng.randint(0, 2**63)
        # Mix the label into the seed for deterministic, label-dependent forking
        label_hash = hash(label) & 0xFFFFFFFFFFFFFFFF
        child_seed = base_seed ^ label_hash
        return SeededRNG(seed=child_seed)


class RNGManager:
    """Manages multiple independent RNG streams for the simulation."""

    def __init__(self, master_seed: int | None = None) -> None:
        self._master = SeededRNG(seed=master_seed)
        self._streams: dict[str, SeededRNG] = {}

    def get_stream(self, name: str) -> SeededRNG:
        """Get or create a named RNG stream."""
        if name not in self._streams:
            self._streams[name] = self._master.fork(name)
        return self._streams[name]

    @property
    def physics(self) -> SeededRNG:
        return self.get_stream("physics")

    @property
    def ai(self) -> SeededRNG:
        return self.get_stream("ai")

    @property
    def injury(self) -> SeededRNG:
        return self.get_stream("injury")

    @property
    def referee(self) -> SeededRNG:
        return self.get_stream("referee")

    @property
    def draft(self) -> SeededRNG:
        return self.get_stream("draft")

    @property
    def general(self) -> SeededRNG:
        return self.get_stream("general")
