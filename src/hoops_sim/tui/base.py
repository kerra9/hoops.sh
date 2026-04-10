"""Rich-only base classes replacing Textual's App, Screen, and Widget.

Provides minimal API-compatible replacements so that widgets and screens
can be constructed and hold state without depending on Textual.  Rendering
is done via Rich Console instead of Textual's compositor.
"""

from __future__ import annotations

import os
import sys
from typing import Any, List, Optional

from rich.console import Console

# Shared console instance
console = Console()


class Widget:
    """Minimal widget base class (Rich-only replacement for textual.widget.Widget)."""

    DEFAULT_CSS = ""

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._widget_name = name
        self._widget_id = id
        self._widget_classes = classes

    def render(self) -> str:
        """Return a Rich-markup string for this widget."""
        return ""

    def refresh(self, **kwargs: Any) -> None:
        """No-op refresh (for API compat with code that calls recompose)."""


class Screen:
    """Minimal screen base class (Rich-only replacement for textual.screen.Screen)."""

    BINDINGS: list[tuple[str, ...]] = []

    def __init__(self) -> None:
        self.app: Optional[App] = None

    def render(self) -> str:
        """Return Rich-markup string for the full screen."""
        return ""

    def notify(self, message: str, **kwargs: Any) -> None:
        """Print a notification to the console."""
        console.print(f"[dim]{message}[/]")


class App:
    """Minimal app class (Rich-only replacement for textual.app.App)."""

    TITLE: str = ""
    SUB_TITLE: str = ""
    CSS_PATH: list[str] = []
    BINDINGS: list[Any] = []

    def __init__(self) -> None:
        self._screen_stack: List[Screen] = []
        self._running = False

    def push_screen(self, screen: Screen) -> None:
        screen.app = self
        self._screen_stack.append(screen)

    def pop_screen(self) -> None:
        if self._screen_stack:
            self._screen_stack.pop()

    def switch_screen(self, screen: Screen) -> None:
        screen.app = self
        if self._screen_stack:
            self._screen_stack[-1] = screen
        else:
            self._screen_stack.append(screen)

    def exit(self) -> None:
        self._running = False

    def notify(self, message: str, **kwargs: Any) -> None:
        console.print(f"[dim]{message}[/]")

    def run(self) -> None:
        """Run the application with a simple input loop."""
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self._running = True
        self.push_screen(MainMenuScreen())

        console.print(f"\n[bold]{self.TITLE}[/] -- {self.SUB_TITLE}\n")

        while self._running and self._screen_stack:
            screen = self._screen_stack[-1]
            rendered = screen.render()
            if rendered:
                console.print(rendered)

            try:
                choice = console.input("[dim]> [/]")
            except (EOFError, KeyboardInterrupt):
                break

            if hasattr(screen, "handle_input"):
                screen.handle_input(choice)
