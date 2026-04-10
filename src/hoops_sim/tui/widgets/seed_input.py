"""Input widget for RNG seed with random-seed button."""

from __future__ import annotations

import random

from hoops_sim.tui.base import Widget


class SeedInput(Widget):
    """Input widget for RNG seed.

    Allows users to enter a specific seed for reproducible simulations
    or generate a random one.
    """

    class SeedChanged:
        """Posted when the seed value changes."""

        def __init__(self, seed: int) -> None:
            self.seed = seed

    def __init__(
        self,
        initial_seed: int | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._seed = initial_seed if initial_seed is not None else random.randint(1, 999999)

    @property
    def seed(self) -> int:
        return self._seed

    def render(self) -> str:
        return f"Seed: {self._seed}  [\U0001f3b2 Random]"

    def randomize(self) -> None:
        """Generate a new random seed."""
        self._seed = random.randint(1, 999999)
