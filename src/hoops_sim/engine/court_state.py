"""Runtime court state: tracks all 10 players and the ball during a game.

This is the missing link between the physics/court systems and the game engine.
Every tick, the simulator reads and writes court state to move the game forward.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from hoops_sim.court.model import get_basket_position, is_three_point
from hoops_sim.court.zones import Zone, get_zone, get_zone_info
from hoops_sim.models.player import Player
from hoops_sim.physical.energy import EnergyState
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    COURT_LENGTH,
    COURT_WIDTH,
    HALF_COURT_LENGTH,
)


class BallStatus(enum.Enum):
    """Current state of the ball."""

    HELD = "held"  # A player has the ball
    IN_AIR = "in_air"  # Shot or pass in flight
    LOOSE = "loose"  # Loose ball / rebound situation
    DEAD = "dead"  # Dead ball (out of bounds, foul, etc.)


@dataclass
class BallState:
    """Tracks the ball's position and status."""

    position: Vec2 = field(default_factory=lambda: Vec2(HALF_COURT_LENGTH, COURT_WIDTH / 2))
    status: BallStatus = BallStatus.DEAD
    holder_id: int | None = None  # Player ID if HELD
    target_pos: Vec2 | None = None  # Target position if IN_AIR (pass/shot)
    target_player_id: int | None = None  # Target player if pass IN_AIR
    ticks_in_air: int = 0  # How many ticks the ball has been airborne


@dataclass
class PlayerCourtState:
    """Runtime state for a single player on the court."""

    player: Player
    position: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    energy: EnergyState = field(default_factory=EnergyState)
    defensive_assignment_id: int | None = None  # Who this player is guarding
    is_on_court: bool = False
    minutes_played: float = 0.0
    fouls: int = 0

    @property
    def player_id(self) -> int:
        return self.player.id


@dataclass
class CourtState:
    """Complete spatial state of all players and the ball on the court.

    Tracks 10 player positions, the ball, and defensive assignments.
    """

    # All players in the game (on court + bench), keyed by player_id
    home_on_court: list[PlayerCourtState] = field(default_factory=list)
    away_on_court: list[PlayerCourtState] = field(default_factory=list)
    home_bench: list[PlayerCourtState] = field(default_factory=list)
    away_bench: list[PlayerCourtState] = field(default_factory=list)

    ball: BallState = field(default_factory=BallState)

    # Which direction each team attacks (True = attacking right basket)
    home_attacks_right: bool = True

    def get_player_state(self, player_id: int) -> PlayerCourtState | None:
        """Find a player's court state by ID across all lists."""
        for pcs in self.all_players():
            if pcs.player_id == player_id:
                return pcs
        return None

    def all_players(self) -> list[PlayerCourtState]:
        """All player states (on court + bench)."""
        return self.home_on_court + self.away_on_court + self.home_bench + self.away_bench

    def all_on_court(self) -> list[PlayerCourtState]:
        """All 10 players currently on the court."""
        return self.home_on_court + self.away_on_court

    def offensive_players(self, home_on_offense: bool) -> list[PlayerCourtState]:
        """Get the 5 offensive players."""
        return self.home_on_court if home_on_offense else self.away_on_court

    def defensive_players(self, home_on_offense: bool) -> list[PlayerCourtState]:
        """Get the 5 defensive players."""
        return self.away_on_court if home_on_offense else self.home_on_court

    def ball_handler(self) -> PlayerCourtState | None:
        """Get the player currently holding the ball."""
        if self.ball.status != BallStatus.HELD or self.ball.holder_id is None:
            return None
        return self.get_player_state(self.ball.holder_id)

    def attacking_right(self, home_on_offense: bool) -> bool:
        """Whether the offensive team is attacking the right basket."""
        if home_on_offense:
            return self.home_attacks_right
        return not self.home_attacks_right

    def basket_position(self, home_on_offense: bool) -> Vec2:
        """Get the basket the offensive team is attacking."""
        return get_basket_position(self.attacking_right(home_on_offense))

    def closest_defender_to(self, position: Vec2, home_on_offense: bool) -> PlayerCourtState | None:
        """Find the closest defensive player to a position."""
        defenders = self.defensive_players(home_on_offense)
        if not defenders:
            return None
        return min(defenders, key=lambda d: d.position.distance_to(position))

    def defender_distance(self, player_id: int, home_on_offense: bool) -> float:
        """Distance from a player to their closest defender."""
        pcs = self.get_player_state(player_id)
        if pcs is None:
            return 99.0
        closest = self.closest_defender_to(pcs.position, home_on_offense)
        if closest is None:
            return 99.0
        return pcs.position.distance_to(closest.position)

    def distance_to_basket(self, player_id: int, home_on_offense: bool) -> float:
        """Distance from a player to the basket they're attacking."""
        pcs = self.get_player_state(player_id)
        if pcs is None:
            return 99.0
        basket = self.basket_position(home_on_offense)
        return pcs.position.distance_to(basket)

    def get_zone_for_player(self, player_id: int, home_on_offense: bool) -> Zone:
        """Determine which shooting zone a player is in."""
        pcs = self.get_player_state(player_id)
        if pcs is None:
            return Zone.DEEP_THREE
        return get_zone(pcs.position, self.attacking_right(home_on_offense))

    def is_three_point_position(self, player_id: int, home_on_offense: bool) -> bool:
        """Check if a player is beyond the three-point line."""
        pcs = self.get_player_state(player_id)
        if pcs is None:
            return False
        return is_three_point(pcs.position, self.attacking_right(home_on_offense))

    def swap_sides(self) -> None:
        """Swap which basket each team attacks (happens at halftime)."""
        self.home_attacks_right = not self.home_attacks_right


def create_initial_positions(
    home_players: list[Player],
    away_players: list[Player],
    home_attacks_right: bool = True,
) -> CourtState:
    """Create initial court state with players in starting positions.

    Places starters on the court and the rest on the bench.
    Assigns basic man-to-man defensive matchups.

    Args:
        home_players: Full home roster (starters first 5).
        away_players: Full away roster (starters first 5).
        home_attacks_right: Direction home team attacks initially.

    Returns:
        Initialized CourtState.
    """
    court = CourtState(home_attacks_right=home_attacks_right)

    # Offensive starting positions (relative to attacking right basket)
    # PG at top of key, SG right wing, SF left wing, PF right elbow, C near paint
    offense_spots_right = [
        Vec2(60.0, 25.0),  # PG: top of key
        Vec2(70.0, 8.0),   # SG: right wing
        Vec2(70.0, 42.0),  # SF: left wing
        Vec2(75.0, 15.0),  # PF: right elbow
        Vec2(82.0, 25.0),  # C: near paint
    ]
    offense_spots_left = [
        Vec2(COURT_LENGTH - p.x, p.y) for p in offense_spots_right
    ]

    # Defensive positions: offset slightly toward basket from offensive spots
    defense_spots_right = [
        Vec2(p.x + 3.0, p.y) for p in offense_spots_right
    ]
    defense_spots_left = [
        Vec2(COURT_LENGTH - p.x, p.y) for p in defense_spots_right
    ]

    home_starters = home_players[:5]
    home_bench_players = home_players[5:]
    away_starters = away_players[:5]
    away_bench_players = away_players[5:]

    # Home team positions
    if home_attacks_right:
        home_spots = offense_spots_right
        away_spots = defense_spots_right
    else:
        home_spots = offense_spots_left
        away_spots = defense_spots_left

    for i, player in enumerate(home_starters):
        pos = home_spots[i] if i < len(home_spots) else Vec2(HALF_COURT_LENGTH, 25.0)
        pcs = PlayerCourtState(
            player=player,
            position=pos,
            energy=EnergyState(
                current=player.max_energy(),
                max_energy=player.max_energy(),
            ),
            is_on_court=True,
        )
        court.home_on_court.append(pcs)

    for i, player in enumerate(away_starters):
        pos = away_spots[i] if i < len(away_spots) else Vec2(HALF_COURT_LENGTH, 25.0)
        pcs = PlayerCourtState(
            player=player,
            position=pos,
            energy=EnergyState(
                current=player.max_energy(),
                max_energy=player.max_energy(),
            ),
            is_on_court=True,
        )
        court.away_on_court.append(pcs)

    # Bench players
    for player in home_bench_players:
        pcs = PlayerCourtState(
            player=player,
            energy=EnergyState(
                current=player.max_energy(),
                max_energy=player.max_energy(),
            ),
            is_on_court=False,
        )
        court.home_bench.append(pcs)

    for player in away_bench_players:
        pcs = PlayerCourtState(
            player=player,
            energy=EnergyState(
                current=player.max_energy(),
                max_energy=player.max_energy(),
            ),
            is_on_court=False,
        )
        court.away_bench.append(pcs)

    # Assign man-to-man defensive matchups
    _assign_defensive_matchups(court)

    return court


def _assign_defensive_matchups(court: CourtState) -> None:
    """Assign basic man-to-man defensive matchups by position index."""
    for i, home_pcs in enumerate(court.home_on_court):
        if i < len(court.away_on_court):
            home_pcs.defensive_assignment_id = court.away_on_court[i].player_id
    for i, away_pcs in enumerate(court.away_on_court):
        if i < len(court.home_on_court):
            away_pcs.defensive_assignment_id = court.home_on_court[i].player_id
