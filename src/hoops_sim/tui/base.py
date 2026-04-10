"""Curses-based base classes replacing Textual's App, Screen, and Widget.

Provides minimal API-compatible replacements so that widgets and screens
can be constructed and hold state without depending on Textual or Rich.
Rendering is done via the Python standard-library curses module.
"""

from __future__ import annotations

import curses
import re
from typing import Any, List, Optional

# ── Rich-markup stripper ─────────────────────────────────────
_MARKUP_RE = re.compile(r"\[/?[^\]]*\]")


def strip_markup(text: str) -> str:
    """Remove Rich-style markup tags like [bold], [#hex], [/] from a string."""
    return _MARKUP_RE.sub("", text)


# ── Hex-to-curses color mapping ──────────────────────────────
_COLOR_PAIR_CACHE: dict[str, int] = {}
_NEXT_PAIR = [1]  # mutable counter; pair 0 is reserved


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #rrggbb to curses 0-1000 RGB."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return int(r / 255 * 1000), int(g / 255 * 1000), int(b / 255 * 1000)


def get_color_pair(hex_color: str) -> int:
    """Return a curses color-pair id for *hex_color*.

    Allocates new curses colors/pairs on the fly when possible.
    Falls back to pair 0 (default) when the terminal has no color support.
    """
    if hex_color in _COLOR_PAIR_CACHE:
        return _COLOR_PAIR_CACHE[hex_color]

    try:
        if not curses.has_colors():
            return 0
        pair_id = _NEXT_PAIR[0]
        if pair_id >= curses.COLOR_PAIRS - 1:
            return 0  # exhausted
        if curses.can_change_color():
            color_id = pair_id + 8  # avoid overwriting the 8 default colors
            r, g, b = _hex_to_rgb(hex_color)
            curses.init_color(color_id, r, g, b)
            curses.init_pair(pair_id, color_id, -1)
        else:
            # Map to closest basic color
            curses.init_pair(pair_id, _closest_basic_color(hex_color), -1)
        _COLOR_PAIR_CACHE[hex_color] = pair_id
        _NEXT_PAIR[0] += 1
        return pair_id
    except Exception:
        return 0


def _closest_basic_color(hex_color: str) -> int:
    """Map a hex color to the nearest curses basic color constant."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # Simple heuristic mapping
    if r > 200 and g < 100 and b < 100:
        return curses.COLOR_RED
    if g > 200 and r < 100 and b < 100:
        return curses.COLOR_GREEN
    if b > 200 and r < 100 and g < 100:
        return curses.COLOR_BLUE
    if r > 200 and g > 200 and b < 100:
        return curses.COLOR_YELLOW
    if r > 200 and g > 100 and b < 100:
        return curses.COLOR_YELLOW
    if r > 200 and g > 200 and b > 200:
        return curses.COLOR_WHITE
    if r < 80 and g < 80 and b < 80:
        return curses.COLOR_BLACK
    if r > 150 and b > 150:
        return curses.COLOR_MAGENTA
    if g > 150 and b > 150:
        return curses.COLOR_CYAN
    return curses.COLOR_WHITE


class Widget:
    """Minimal widget base class (curses-compatible)."""

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
        """Return a plain-text string for this widget.

        May contain Rich-style markup; the app layer will strip it
        before writing to curses.
        """
        return ""

    def refresh(self, **kwargs: Any) -> None:
        """No-op refresh (for API compat with code that calls recompose)."""


class Screen:
    """Minimal screen base class (curses-compatible)."""

    BINDINGS: list[tuple[str, ...]] = []

    def __init__(self) -> None:
        self.app: Optional[App] = None

    def render(self) -> str:
        """Return plain-text (possibly with Rich markup) for the full screen."""
        return ""

    def notify(self, message: str, **kwargs: Any) -> None:
        """Store notification for display on next refresh."""


class App:
    """Minimal app class using curses for terminal rendering."""

    TITLE: str = ""
    SUB_TITLE: str = ""
    CSS_PATH: list[str] = []
    BINDINGS: list[Any] = []

    def __init__(self) -> None:
        self._screen_stack: List[Screen] = []
        self._running = False
        self._stdscr: Any = None

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
        pass

    def run(self) -> None:
        """Run the application inside a curses wrapper."""
        curses.wrapper(self._main)

    def _main(self, stdscr: Any) -> None:
        """Main curses loop."""
        self._stdscr = stdscr
        curses.curs_set(0)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self._running = True
        first = MainMenuScreen()
        first.app = self
        self._screen_stack = [first]

        while self._running and self._screen_stack:
            screen = self._screen_stack[-1]
            screen.app = self

            stdscr.clear()

            # Header
            max_y, max_x = stdscr.getmaxyx()
            header = f" {self.TITLE} -- {self.SUB_TITLE} "
            try:
                stdscr.addstr(0, 0, header[:max_x], curses.A_BOLD | curses.A_REVERSE)
            except curses.error:
                pass

            # Render screen content
            rendered = strip_markup(screen.render())
            lines = rendered.split("\n")
            for i, line in enumerate(lines[: max_y - 3], start=2):
                try:
                    stdscr.addstr(i, 0, line[: max_x - 1])
                except curses.error:
                    pass

            # Footer prompt
            try:
                stdscr.addstr(max_y - 1, 0, " > ", curses.A_BOLD)
            except curses.error:
                pass

            stdscr.refresh()

            # Read input
            try:
                ch = stdscr.getch()
            except KeyboardInterrupt:
                break

            if ch == -1:
                continue

            choice = chr(ch) if 0 <= ch < 256 else ""

            if hasattr(screen, "handle_input"):
                screen.handle_input(choice)
