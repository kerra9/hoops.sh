"""Court spatial model: zones, positions, dimensions."""

from hoops_sim.court.model import (
    CourtDimensions,
    distance_to_basket,
    get_basket_position,
    is_in_bounds,
    is_in_frontcourt,
    is_in_paint,
    is_in_restricted_area,
    is_three_point,
)
from hoops_sim.court.zones import Zone, ZoneInfo, get_zone, get_zone_info

__all__ = [
    "CourtDimensions",
    "Zone",
    "ZoneInfo",
    "distance_to_basket",
    "get_basket_position",
    "get_zone",
    "get_zone_info",
    "is_in_bounds",
    "is_in_frontcourt",
    "is_in_paint",
    "is_in_restricted_area",
    "is_three_point",
]
