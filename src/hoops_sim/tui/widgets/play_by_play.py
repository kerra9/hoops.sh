"""Scrolling narration log consuming NarrationEvent objects.

Enhanced with structured formatting, timestamps, and color-coded event types.
"""

from __future__ import annotations

from typing import List

from hoops_sim.narration.engine import NarrationEvent, NarrationIntensity
from hoops_sim.tui.base import Widget
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

    Consumes NarrationEvent objects and supports intensity-based coloring
    with structured formatting.
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
        self._lines: List[str] = []

    def add_event(self, event: NarrationEvent) -> None:
        """Add a narration event with structured formatting."""
        self._events.append(event)
        color = _event_color(event)
        if event.is_milestone:
            self._lines.append(f"[{color}]\u2605 \u2550\u2550 {event.text} \u2550\u2550[/]")
        else:
            self._lines.append(f"[{color}]\u2022 {event.text}[/]")

    def add_text(
        self, text: str, intensity: NarrationIntensity = NarrationIntensity.MEDIUM
    ) -> None:
        """Add raw text to the play-by-play log."""
        self.add_event(NarrationEvent(text=text, intensity=intensity))

    def clear(self) -> None:
        """Clear the play-by-play log."""
        self._events.clear()
        self._lines.clear()

    def render(self) -> str:
        """Return the last N lines of play-by-play."""
        return "\n".join(self._lines[-20:])
