"""Scrolling narration log consuming NarrationEvent objects.

Textual widget using RichLog for auto-scrolling, color-coded play-by-play.
"""

from __future__ import annotations

from rich.text import Text
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


class PlayByPlayWidget(Widget):
    """Scrolling narration log for play-by-play text.

    Uses Textual's RichLog widget for auto-scrolling with the ability
    to scroll back, and color-coded event lines.
    """

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="pbp-log")

    @property
    def log(self) -> RichLog:
        return self.query_one("#pbp-log", RichLog)

    def add_event(self, event: NarrationEvent) -> None:
        """Add a narration event with structured formatting."""
        color = _event_color(event)
        if event.is_milestone:
            styled = Text(f"\u2605 \u2550\u2550 {event.text} \u2550\u2550", style=color)
        else:
            styled = Text(f"\u2022 {event.text}", style=color)
        self.log.write(styled)

    def add_text(
        self, text: str, intensity: NarrationIntensity = NarrationIntensity.MEDIUM
    ) -> None:
        """Add raw text to the play-by-play log."""
        self.add_event(NarrationEvent(text=text, intensity=intensity))

    def clear(self) -> None:
        """Clear the play-by-play log."""
        self.log.clear()


# Keep backward-compatible alias
PlayByPlay = PlayByPlayWidget
