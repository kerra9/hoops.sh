"""Compatibility shim -- re-exports Textual base classes.

The old hand-rolled curses framework is replaced by Textual.
This module exists only for backward compatibility with any
code that imports from hoops_sim.tui.base.
"""

from __future__ import annotations

import re

from textual.app import App
from textual.screen import Screen
from textual.widget import Widget

__all__ = ["App", "Screen", "Widget", "strip_markup"]

# Rich-markup stripper kept for utility use in non-widget contexts
_MARKUP_RE = re.compile(r"\[/?[^\]]*\]")


def strip_markup(text: str) -> str:
    """Remove Rich-style markup tags like [bold], [#hex], [/] from a string."""
    return _MARKUP_RE.sub("", text)
