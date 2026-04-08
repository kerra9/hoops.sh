"""Settings screen for sim speed, narration verbosity, display preferences."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select, Switch


class SettingsScreen(Screen):
    """Settings for sim speed and display preferences."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="settings-screen"):
            with Vertical(id="settings-form"):
                yield Label("Settings", id="settings-title")
                yield Label("")
                yield Label("Sim Speed (ms between ticks):")
                yield Select(
                    [
                        ("Instant (0ms)", 0),
                        ("Fast (50ms)", 50),
                        ("Normal (100ms)", 100),
                        ("Slow (250ms)", 250),
                        ("Very Slow (500ms)", 500),
                    ],
                    value=100,
                    id="sim-speed",
                )
                yield Label("")
                yield Label("Narration Verbosity:")
                yield Select(
                    [
                        ("Minimal", "minimal"),
                        ("Normal", "normal"),
                        ("Verbose", "verbose"),
                    ],
                    value="normal",
                    id="narration-verbosity",
                )
                yield Label("")
                yield Button("Back", id="btn-back", variant="default")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
