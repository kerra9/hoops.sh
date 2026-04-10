"""Scrolling narration log consuming NarrationEvent objects.

Enhanced with structured formatting, timestamps, and color-coded event types.
"""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import RichLog

from hoops_sim.narration.engine import NarrationEvent, NarrationIntensity
from hoops_sim.tui.theme import (
    PBP_DEFAULT,
    PBP_LOW,
    PBP_MILESTONE,
    PBP_SCORE,
    PBP_TURNOVER,
)

INTENSITY_COLORS = {
    NarrationIntensity.LOW: PBP_LOW,
    NarrationIntensity.MEDIUM: PBP_DEFAULT,
    NarrationIntensity.HIGH: PBP_SCORE,
    NarrationIntensity.MAXIMUM: PBP_MILESTONE,
}

# Keywords for event type color coding
_SCORE_KEYWORDS = {"got it", "swish", "bucket", "layup", "dunk", "three", "scores", "makes"}
_TURNOVER_KEYWORDS = {"turnover", "stolen", "intercepted", "travel", "violation"}
_BLOCK_KEYWORDS = {"blocked", "rejection", "swatted"}


def _event_color(event: NarrationEvent) -> str:
    """Determine color based on event text content."""
    text_lower = event.text.lower()
    if event.is_milestone:
        return PBP_MILESTONE
    if any(kw in text_lower for kw in _SCORE_KEYWORDS):
        return PBP_SCORE
    if any(kw in text_lower for kw in _TURNOVER_KEYWORDS):
        return PBP_TURNOVER
    if any(kw in text_lower for kw in _BLOCK_KEYWORDS):
        return "#e67e22"
    return INTENSITY_COLORS.get(event.intensity, PBP_DEFAULT)


class PlayByPlay(Widget):
    """Scrolling narration log for play-by-play text.

    Consumes NarrationEvent objects, auto-scrolls,
    and supports intensity-based coloring with structured formatting.
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
        """Add a narration event with structured formatting."""
        self._events.append(event)
        try:
            log = self.query_one("#pbp-log", RichLog)
            color = _event_color(event)

            if event.is_milestone:
                # Milestone events get special formatting
                log.write(f"[{color}]\u2605 \u2550\u2550 {event.text} \u2550\u2550[/]")
            else:
                prefix = "\u2022 "
                log.write(f"[{color}]{prefix}{event.text}[/]")
        except Exception:
            pass

    def add_text(
        self, text: str, intensity: NarrationIntensity = NarrationIntensity.MEDIUM
    ) -> None:
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
