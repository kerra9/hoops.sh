"""Math utility functions."""

from __future__ import annotations


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value between lo and hi (inclusive)."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t in [0, 1]."""
    return a + (b - a) * clamp(t, 0.0, 1.0)


def inverse_lerp(a: float, b: float, value: float) -> float:
    """Inverse linear interpolation: returns t such that lerp(a, b, t) == value."""
    if abs(b - a) < 1e-10:
        return 0.0
    return clamp((value - a) / (b - a), 0.0, 1.0)


def remap(value: float, from_lo: float, from_hi: float, to_lo: float, to_hi: float) -> float:
    """Remap a value from one range to another."""
    t = inverse_lerp(from_lo, from_hi, value)
    return lerp(to_lo, to_hi, t)


def attribute_to_range(attribute: int, lo: float, hi: float) -> float:
    """Convert a 0-99 attribute value to a float in the range [lo, hi]."""
    return remap(float(attribute), 0.0, 99.0, lo, hi)
