"""Input widget for RNG seed with random-seed button."""

from __future__ import annotations

import random

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label


class SeedInput(Widget):
    """Input widget for RNG seed with a randomize button.

    Allows users to enter a specific seed for reproducible simulations
    or generate a random one.
    """

    DEFAULT_CSS = """
    SeedInput {
        height: 3;
        layout: horizontal;
        width: 100%;
    }
    """

    class SeedChanged(Message):
        """Posted when the seed value changes."""

        def __init__(self, seed: int) -> None:
            super().__init__()
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

    def compose(self) -> ComposeResult:
        with Horizontal(classes="seed-input"):
            yield Label("Seed: ")
            yield Input(
                value=str(self._seed),
                placeholder="Enter seed...",
                type="integer",
                id="seed-value",
            )
            yield Button("\U0001f3b2 Random", id="btn-random-seed", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-random-seed":
            self._seed = random.randint(1, 999999)
            inp = self.query_one("#seed-value", Input)
            inp.value = str(self._seed)
            self.post_message(self.SeedChanged(self._seed))

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            self._seed = int(event.value)
            self.post_message(self.SeedChanged(self._seed))
        except ValueError:
            pass
