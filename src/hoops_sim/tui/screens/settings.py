"""Settings screen for sim speed, narration verbosity, display preferences.

Redesigned with grouped settings sections and toggle switches.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select, Switch


class SettingsScreen(Screen):
    """Settings for sim speed and display preferences.

    Features:
    - Grouped settings in sections
    - Select widgets for sim speed and narration
    - Toggle switches for auto-save and other options
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="settings-screen"):
            with Vertical(id="settings-form"):
                yield Label("[bold]Settings[/]", id="settings-title")

                # Simulation section
                yield Label("")
                yield Label("[bold green]SIMULATION[/]")
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

                # Display section
                yield Label("")
                yield Label("[bold blue]DISPLAY[/]")
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

                # Auto-save section
                yield Label("")
                yield Label("[bold yellow]AUTO-SAVE[/]")
                yield Label("Auto-save after each game:")
                yield Switch(value=True, id="auto-save-switch")

                yield Label("")
                yield Button("Back", id="btn-back", variant="default")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
