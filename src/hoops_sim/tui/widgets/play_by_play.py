"""Scrolling narration log consuming NarrationEvent objects."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

from hoops_sim.narration.engine import NarrationEvent, NarrationIntensity

INTENSITY_COLORS = {
    NarrationIntensity.LOW: "#888888",
    NarrationIntensity.MEDIUM: "#cccccc",
    NarrationIntensity.HIGH: "#f1c40f",
    NarrationIntensity.MAXIMUM: "#e74c3c",
}


class PlayByPlay(Widget):
    """Scrolling narration log for play-by-play text.

    Consumes NarrationEvent objects, auto-scrolls,
    and supports intensity-based coloring.
    """

    DEFAULT_CSS = """
    PlayByPlay {
        height: 100%;
        width: 100%;
    }
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._events: List[NarrationEvent] = []

    def compose(self) -> ComposeResult:
        yield RichLog(id="pbp-log", wrap=True, highlight=True, auto_scroll=True)

    def add_event(self, event: NarrationEvent) -> None:
        """Add a narration event to the play-by-play log."""
        self._events.append(event)
        try:
            log = self.query_one("#pbp-log", RichLog)
            color = INTENSITY_COLORS.get(event.intensity, "#cccccc")
            prefix = "\u2605 " if event.is_milestone else "  "
            log.write(f"[{color}]{prefix}{event.text}[/]")
        except Exception:
            pass

    def add_text(self, text: str, intensity: NarrationIntensity = NarrationIntensity.MEDIUM) -> None:
        """Add raw text to the play-by-play log."""
        self.add_event(NarrationEvent(text=text, intensity=intensity))

    def clear(self) -> None:
        """Clear the play-by-play log."""
        self._events.clear()
        try:
            log = self.query_one("#pbp-log", RichLog)
            log.clear()
        except Exception:
            pass
