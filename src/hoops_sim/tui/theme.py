"""Color constants and team palettes for the hoops.sh TUI.

Centralizes all color definitions so they can be referenced from
widgets, TCSS variables, and Rich markup consistently.
"""

from __future__ import annotations

# ── Court colors ──────────────────────────────────────────────
COURT_WOOD = "#c4873b"
COURT_LINES = "#ffffff"
PAINT = "#1a3a5c"
THREE_POINT_LINE = "#ffffff"

# ── Shooting zone heat map ────────────────────────────────────
HOT_ZONE = "#e74c3c"
COLD_ZONE = "#3498db"
NEUTRAL_ZONE = "#555555"

# ── Score / result colors ─────────────────────────────────────
SCORE_GREEN = "#2ecc71"
SCORE_RED = "#e74c3c"
SCORE_GOLD = "#ffd700"

# ── Badge tier colors ─────────────────────────────────────────
BADGE_BRONZE = "#cd7f32"
BADGE_SILVER = "#c0c0c0"
BADGE_GOLD = "#ffd700"
BADGE_HOF = "#9b59b6"

# ── Energy / fatigue colors ───────────────────────────────────
ENERGY_FRESH = "#2ecc71"
ENERGY_LIGHT = "#f1c40f"
ENERGY_MODERATE = "#e67e22"
ENERGY_HEAVY = "#e74c3c"
ENERGY_EXHAUSTED = "#c0392b"
ENERGY_GASSED = "#8b0000"

# ── Momentum colors ──────────────────────────────────────────
MOMENTUM_HOME = "#2ecc71"
MOMENTUM_AWAY = "#e74c3c"
MOMENTUM_NEUTRAL = "#888888"

# ── Attribute rating colors ───────────────────────────────────
RATING_ELITE = "#2ecc71"
RATING_GREAT = "#27ae60"
RATING_GOOD = "#f1c40f"
RATING_AVERAGE = "#e67e22"
RATING_BELOW_AVG = "#e74c3c"
RATING_POOR = "#c0392b"

# ── UI accent colors ─────────────────────────────────────────
ACCENT_PRIMARY = "#3498db"
ACCENT_SUCCESS = "#2ecc71"
ACCENT_WARNING = "#f1c40f"
ACCENT_ERROR = "#e74c3c"
ACCENT_MUTED = "#888888"
ACCENT_DIM = "#555555"

# ── Playoff picture colors ───────────────────────────────────
PLAYOFF_IN = "#2ecc71"
PLAYOFF_PLAYIN = "#f1c40f"
PLAYOFF_OUT = "#e74c3c"

# ── Play-by-play event colors ────────────────────────────────
PBP_SCORE = "#ffd700"
PBP_TURNOVER = "#e74c3c"
PBP_BLOCK = "#e67e22"
PBP_STEAL = "#e67e22"
PBP_FOUL = "#c0392b"
PBP_MILESTONE = "#9b59b6"
PBP_DEFAULT = "#cccccc"
PBP_LOW = "#888888"

# ── Banner gradient colors ────────────────────────────────────
BANNER_GRADIENT = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6"]


def rating_color(value: int) -> str:
    """Return a color string based on rating value (0-99)."""
    if value >= 90:
        return RATING_ELITE
    if value >= 80:
        return RATING_GREAT
    if value >= 70:
        return RATING_GOOD
    if value >= 60:
        return RATING_AVERAGE
    if value >= 50:
        return RATING_BELOW_AVG
    return RATING_POOR


def energy_color(pct: float) -> str:
    """Return a color string based on energy percentage (0.0-1.0)."""
    if pct >= 0.85:
        return ENERGY_FRESH
    if pct >= 0.70:
        return ENERGY_LIGHT
    if pct >= 0.50:
        return ENERGY_MODERATE
    if pct >= 0.30:
        return ENERGY_HEAVY
    if pct >= 0.15:
        return ENERGY_EXHAUSTED
    return ENERGY_GASSED


def fg_pct_color(pct: float) -> str:
    """Return a color for field goal percentage display."""
    if pct >= 0.50:
        return SCORE_GREEN
    if pct >= 0.40:
        return ACCENT_WARNING
    if pct >= 0.30:
        return ACCENT_MUTED
    return SCORE_RED
