"""Settings screen for sim speed, narration verbosity, display preferences.

Textual Screen with Switch, Select, and Input widgets.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select, Static, Switch


class SettingsScreen(Screen):
    """Settings for sim speed and display preferences."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="settings-form"):
                yield Static("[bold]Settings[/]", markup=True)

                yield Static("\n[bold green]SIMULATION[/]", markup=True)
                yield Label("Sim Speed:")
                yield Select(
                    [
                        ("Instant (0ms)", 0),
                        ("Fast (50ms)", 50),
                        ("Normal (100ms)", 100),
                        ("Slow (250ms)", 250),
                        ("Very Slow (500ms)", 500),
                    ],
                    value=100,
                    id="speed-select",
                )

                yield Static("\n[bold blue]DISPLAY[/]", markup=True)
                yield Label("Narration Verbosity:")
                yield Select(
                    [
                        ("Minimal", "minimal"),
                        ("Normal", "normal"),
                        ("Verbose", "verbose"),
                    ],
                    value="normal",
                    id="narration-select",
                )

                yield Static("\n[bold yellow]AUTO-SAVE[/]", markup=True)
                yield Label("Auto-save after each game:")
                yield Switch(value=True, id="autosave-switch")

                yield Static("\n[bold]THEME[/]", markup=True)
                yield Label("Dark Mode:")
                yield Switch(value=True, id="dark-mode-switch")

                yield Button("Back", variant="error", id="btn-back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "dark-mode-switch":
            self.app.dark = event.value

    def action_go_back(self) -> None:
        self.app.pop_screen()
