"""GameSimulator: the real basketball simulation engine.

Owns the full game loop and wires together all subsystems:
- GameState / GameClock (clock management)
- CourtState (player positions, ball state)
- Player AI (ball handler decisions)
- Shot Probability (18-factor calculator)
- Energy/Fatigue system
- Coach AI (substitutions, timeouts)
- Narration engine
- Momentum/Confidence tracking

The simulation runs at the **possession level**: each possession resolves
through 1-4 action cycles (pass, dribble, shoot) that consume realistic
game-clock time. This keeps the simulator fast while still using the full
depth of the subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.ai.coach_brain import (
    evaluate_substitution_need,
    should_call_timeout,
)
from hoops_sim.ai.player_brain import ActionOption, evaluate_ball_handler_options
from hoops_sim.court.driving_lanes import analyze_driving_lane
from hoops_sim.court.model import get_basket_position
from hoops_sim.court.passing_lanes import analyze_passing_lane
from hoops_sim.court.zones import Zone, get_zone, get_zone_info
from hoops_sim.engine.court_state import (
    BallStatus,
    CourtState,
    PlayerCourtState,
    create_initial_positions,
)
from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.possession import PossessionState
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.models.team import Team
from hoops_sim.narration.engine import NarrationEngine, NarrationEvent
from hoops_sim.physics.vec import Vec2
from hoops_sim.psychology.confidence import ConfidenceTracker
from hoops_sim.psychology.momentum import MomentumTracker
from hoops_sim.shot.probability import ShotContext, calculate_shot_probability
from hoops_sim.utils.constants import (
    COURT_LENGTH,
    COURT_WIDTH,
    ENERGY_DRAIN_JOG,
    ENERGY_DRAIN_SPRINT,
    ENERGY_RECOVERY_BENCH,
    TICK_DURATION,
)
from hoops_sim.utils.math import attribute_to_range, clamp
from hoops_sim.utils.rng import RNGManager


@dataclass
class SimEvent:
    """An event produced by the simulator for the UI/narration layer."""

    narration: NarrationEvent | None = None
    event_type: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class GameResult:
    """Final result of a simulated game."""

    home_score: int = 0
    away_score: int = 0
    home_stats: TeamGameStats = field(default_factory=TeamGameStats)
    away_stats: TeamGameStats = field(default_factory=TeamGameStats)
    events: list[SimEvent] = field(default_factory=list)
    total_possessions: int = 0


class GameSimulator:
    """The real basketball simulation engine.

    Simulates at the possession level: each possession goes through
    1-4 action cycles where the ball handler AI decides what to do,
    and the action is resolved using the full subsystem stack.
    """

    def __init__(
        self,
        home_team: Team,
        away_team: Team,
        seed: int = 42,
        narrate: bool = True,
    ) -> None:
        self.home_team = home_team
        self.away_team = away_team
        self.narrate = narrate

        # RNG streams
        self._rng_mgr = RNGManager(master_seed=seed)
        self._rng = self._rng_mgr.general
        self._ai_rng = self._rng_mgr.ai
        self._phys_rng = self._rng_mgr.physics

        # Game state
        self.game_state = GameState(home_team=home_team, away_team=away_team)

        # Court state with player positions
        home_sorted = sorted(home_team.roster, key=lambda p: p.overall, reverse=True)
        away_sorted = sorted(away_team.roster, key=lambda p: p.overall, reverse=True)
        self.court = create_initial_positions(home_sorted, away_sorted)

        # Subsystems
        self.narration = NarrationEngine(self._rng) if narrate else None
        self.momentum = MomentumTracker()
        self.confidence = ConfidenceTracker()

        # Stats
        self.home_stats = TeamGameStats(team_id=home_team.id, team_name=home_team.full_name)
        self.away_stats = TeamGameStats(team_id=away_team.id, team_name=away_team.full_name)
        for p in home_team.roster:
            self.home_stats.add_player(p.id, p.full_name)
        for p in away_team.roster:
            self.away_stats.add_player(p.id, p.full_name)

        # Internal state
        self._events: list[SimEvent] = []
        self._game_over = False
        self._opponent_run = 0
        self._own_turnovers_recent: list[bool] = []
        self._total_possessions = 0
        self._quarter = 0
        self._last_passer_id: int | None = None

    # -- Public API -----------------------------------------------------------

    def simulate_full_game(self) -> GameResult:
        """Simulate an entire game and return the result."""
        self._start_game()
        while not self._game_over:
            self._simulate_possession()
        return GameResult(
            home_score=self.game_state.score.home,
            away_score=self.game_state.score.away,
            home_stats=self.home_stats,
            away_stats=self.away_stats,
            events=self._events,
            total_possessions=self._total_possessions,
        )

    def step(self) -> list[SimEvent]:
        """Simulate one possession and return events. For TUI rendering."""
        if self._game_over:
            return []
        if self.game_state.phase == GamePhase.PRE_GAME:
            self._start_game()
        before = len(self._events)
        self._simulate_possession()
        return self._events[before:]

    @property
    def is_game_over(self) -> bool:
        return self._game_over

    # -- Game flow ------------------------------------------------------------

    def _start_game(self) -> None:
        """Initialize the game."""
        self._quarter = 1
        gs = self.game_state
        gs.start_quarter(1)
        gs.clock.start()
        gs.phase = GamePhase.QUARTER

        # Tip-off
        home_starts = self._rng.random() < 0.5
        self._off_team_id = self.home_team.id if home_starts else self.away_team.id
        self._def_team_id = self.away_team.id if home_starts else self.home_team.id

    def _simulate_possession(self) -> None:
        """Simulate a single possession from inbound to resolution."""
        gs = self.game_state

        if self._game_over:
            return

        self._total_possessions += 1
        home_on_offense = self._off_team_id == self.home_team.id
        is_home = home_on_offense

        # Set up the possession
        self._setup_possession(home_on_offense)

        # Consume 5-14 seconds of clock time for the play to develop
        # NBA average possession length is ~14 seconds
        setup_time = self._rng.uniform(5.0, 14.0)
        self._advance_clock(setup_time)

        # Check quarter end after setup time
        if self._check_quarter_end():
            return

        # Drain energy for on-court players during setup
        self._drain_energy_for_time(setup_time)

        # Get the ball handler and run 1-3 action cycles
        max_actions = self._rng.randint(1, 3)
        for action_num in range(max_actions):
            handler = self._get_ball_handler(home_on_offense)
            if handler is None:
                break

            # Run the player AI, with pass bias on first action
            action = self._run_player_ai(handler, home_on_offense)

            # First action: force a pass 60% of the time to distribute the ball
            if action_num == 0 and max_actions > 1 and action.action == "shoot":
                pass_quals = self._eval_pass_qualities(handler, home_on_offense)
                if pass_quals and self._rng.random() < 0.60:
                    best_pass = max(pass_quals, key=lambda pq: pq[1])
                    action = ActionOption("pass", 0.5, target_id=best_pass[0])

            if action.action == "shoot":
                self._execute_shot(handler, home_on_offense, action_num > 0)
                self._end_possession_and_flip()
                return

            elif action.action == "drive":
                resolved = self._execute_drive(handler, home_on_offense)
                if resolved:
                    self._end_possession_and_flip()
                    return
                # Drive didn't resolve (kicked out) -- continue to next action

            elif action.action == "pass" and action.target_id is not None:
                stolen = self._execute_pass(handler, action.target_id, home_on_offense)
                if stolen:
                    self._end_possession_and_flip()
                    return
                # Successful pass -- consume 1-2 seconds, continue
                pass_time = self._rng.uniform(1.0, 2.5)
                self._advance_clock(pass_time)
                if self._check_quarter_end():
                    return

            elif action.action == "post_up":
                self._execute_post_up(handler, home_on_offense)
                self._end_possession_and_flip()
                return

            else:
                # Hold: consume time
                hold_time = self._rng.uniform(1.5, 3.0)
                self._advance_clock(hold_time)
                if self._check_quarter_end():
                    return

        # If we exhausted all action cycles without resolving, take a shot
        handler = self._get_ball_handler(home_on_offense)
        if handler:
            self._execute_shot(handler, home_on_offense, catch_and_shoot=False)
        self._end_possession_and_flip()

    def _setup_possession(self, home_on_offense: bool) -> None:
        """Reset positions and state for a new possession."""
        gs = self.game_state
        gs.possession.new_possession(self._off_team_id, self._def_team_id)
        gs.possession.transition_to(PossessionState.LIVE)
        gs.clock.reset_shot_clock()
        gs.clock.start()
        self._last_passer_id = None

        # Place players in half-court positions
        self._reset_positions(home_on_offense)

        # Give ball to a random offensive player, weighted by playmaking
        offense = self.court.offensive_players(home_on_offense)
        if offense:
            weights = [
                max(1, p.player.attributes.playmaking.ball_handle
                    + p.player.attributes.playmaking.pass_vision)
                for p in offense
            ]
            handler = self._rng.choices(offense, weights=weights, k=1)[0]
            self.court.ball.holder_id = handler.player_id
            self.court.ball.status = BallStatus.HELD

        # Coach AI between possessions
        self._check_coach_decisions(home_on_offense)
        self.confidence.decay_all()
        self.momentum.decay()

    def _end_possession_and_flip(self) -> None:
        """Flip possession to the other team."""
        old_off = self._off_team_id
        old_def = self._def_team_id
        self._off_team_id = old_def
        self._def_team_id = old_off

    def _advance_clock(self, seconds: float) -> None:
        """Advance the game clock by the given seconds."""
        gs = self.game_state
        gs.clock.game_clock = max(0.0, gs.clock.game_clock - seconds)
        gs.clock.shot_clock = max(0.0, gs.clock.shot_clock - seconds)

    def _check_quarter_end(self) -> bool:
        """Check if the quarter has ended and handle it."""
        gs = self.game_state
        if gs.clock.game_clock > 0.0:
            return False

        self._quarter += 1

        if self.narration:
            event = self.narration.narrate_quarter_end(
                quarter=self._quarter - 1,
                home_team=self.home_team.full_name,
                away_team=self.away_team.full_name,
                home_score=gs.score.home,
                away_score=gs.score.away,
            )
            self._emit("quarter_end", event, {"quarter": self._quarter - 1})

        # Check game over (after Q4+ if not tied)
        if self._quarter > 4 and gs.score.home != gs.score.away:
            gs.phase = GamePhase.POST_GAME
            self._game_over = True
            return True

        # Halftime swap
        if self._quarter == 3:
            self.court.swap_sides()
            for pcs in self.court.all_players():
                pcs.energy.recover(25.0)

        # Start next quarter
        gs.start_quarter(self._quarter)
        gs.clock.start()

        # Alternate possession
        if self._quarter % 2 == 0:
            self._off_team_id = self.away_team.id
            self._def_team_id = self.home_team.id
        else:
            self._off_team_id = self.home_team.id
            self._def_team_id = self.away_team.id

        return True

    # -- Positioning ----------------------------------------------------------

    def _reset_positions(self, home_on_offense: bool) -> None:
        """Place players in half-court offensive/defensive positions."""
        attacking_right = self.court.attacking_right(home_on_offense)
        offense = self.court.offensive_players(home_on_offense)
        defense = self.court.defensive_players(home_on_offense)
        basket = self.court.basket_position(home_on_offense)

        if attacking_right:
            spots = [
                Vec2(60.0, 25.0), Vec2(70.0, 8.0), Vec2(70.0, 42.0),
                Vec2(75.0, 15.0), Vec2(82.0, 25.0),
            ]
        else:
            spots = [
                Vec2(34.0, 25.0), Vec2(24.0, 8.0), Vec2(24.0, 42.0),
                Vec2(19.0, 15.0), Vec2(12.0, 25.0),
            ]

        for i, pcs in enumerate(offense):
            if i < len(spots):
                base = spots[i]
                pcs.position = Vec2(
                    clamp(base.x + self._rng.gauss(0, 2.0), 0, COURT_LENGTH),
                    clamp(base.y + self._rng.gauss(0, 2.0), 0, COURT_WIDTH),
                )

        for i, dcs in enumerate(defense):
            if i < len(offense):
                off_pos = offense[i].position
                to_basket = (basket - off_pos).normalized()
                dcs.position = Vec2(
                    clamp(off_pos.x + to_basket.x * 3.0 + self._rng.gauss(0, 1.0),
                          0, COURT_LENGTH),
                    clamp(off_pos.y + to_basket.y * 3.0 + self._rng.gauss(0, 1.0),
                          0, COURT_WIDTH),
                )

    # -- Player AI ------------------------------------------------------------

    def _get_ball_handler(self, home_on_offense: bool) -> PlayerCourtState | None:
        """Get the current ball handler."""
        if self.court.ball.holder_id is not None:
            return self.court.get_player_state(self.court.ball.holder_id)
        offense = self.court.offensive_players(home_on_offense)
        if offense:
            self.court.ball.holder_id = offense[0].player_id
            return offense[0]
        return None

    def _run_player_ai(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> ActionOption:
        """Run the player brain AI for the current ball handler."""
        gs = self.game_state
        player = handler.player
        basket = self.court.basket_position(home_on_offense)

        shot_quality = self._eval_shot_quality(handler, home_on_offense)
        drive_quality = self._eval_drive_quality(handler, home_on_offense)
        pass_qualities = self._eval_pass_qualities(handler, home_on_offense)

        post_quality = 0.0
        if (handler.position.distance_to(basket) < 15.0
                and player.attributes.finishing.post_moves > 60):
            post_quality = player.attributes.finishing.post_moves / 100.0 * 0.7

        shot_clock_pct = gs.clock.shot_clock / 24.0

        return evaluate_ball_handler_options(
            shot_quality=shot_quality,
            drive_quality=drive_quality,
            pass_qualities=pass_qualities,
            post_quality=post_quality,
            shot_volume_tendency=player.tendencies.shot_volume,
            drive_tendency=player.tendencies.drive_tendency,
            pass_first_tendency=player.tendencies.pass_first,
            post_up_tendency=player.tendencies.post_up_tendency,
            shot_clock_pct=shot_clock_pct,
            confidence=self.confidence.shooting_modifier(player.id),
            basketball_iq=player.attributes.mental.basketball_iq,
            rng=self._ai_rng,
        )

    def _eval_shot_quality(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> float:
        player = handler.player
        basket = self.court.basket_position(home_on_offense)
        dist = handler.position.distance_to(basket)
        attacking_right = self.court.attacking_right(home_on_offense)
        zone = get_zone(handler.position, attacking_right)
        base_rating = player.get_zone_rating(zone.name)
        def_dist = self.court.defender_distance(handler.player_id, home_on_offense)

        # Openness: 0 if defender <2ft, 1 if >8ft. Typical defender distance is 3-5ft
        openness = clamp((def_dist - 2.0) / 6.0, 0.0, 1.0)

        rating_factor = base_rating / 99.0
        # Distance penalty: shots from far away are less desirable
        distance_penalty = clamp((dist - 4.0) / 25.0, 0.0, 0.5)

        quality = rating_factor * 0.35 + openness * 0.40 + (0.5 - distance_penalty) * 0.25
        return clamp(quality, 0.0, 1.0)

    def _eval_drive_quality(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> float:
        player = handler.player
        basket = self.court.basket_position(home_on_offense)
        closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
        if closest_def is None:
            return 0.9
        all_defs = self.court.defensive_players(home_on_offense)
        help_pos = [d.position for d in all_defs if d.player_id != closest_def.player_id]
        result = analyze_driving_lane(
            driver_pos=handler.position,
            basket_pos=basket,
            primary_defender_pos=closest_def.position,
            help_defender_positions=help_pos,
        )
        drive_skill = (
            player.attributes.athleticism.speed * 0.3
            + player.attributes.playmaking.speed_with_ball * 0.3
            + player.attributes.finishing.layup * 0.2
            + player.attributes.finishing.driving_dunk * 0.2
        ) / 99.0
        return clamp(result.quality * 0.6 + drive_skill * 0.4, 0.0, 1.0)

    def _eval_pass_qualities(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> list[tuple[int, float]]:
        teammates = self.court.offensive_players(home_on_offense)
        defenders = self.court.defensive_players(home_on_offense)
        def_positions = [d.position for d in defenders]
        basket = self.court.basket_position(home_on_offense)
        qualities: list[tuple[int, float]] = []
        for tm in teammates:
            if tm.player_id == handler.player_id:
                continue
            lane = analyze_passing_lane(
                passer_pos=handler.position,
                receiver_pos=tm.position,
                defender_positions=def_positions,
            )
            recv_dist = tm.position.distance_to(basket)
            recv_def = self.court.defender_distance(tm.player_id, home_on_offense)
            openness = clamp(recv_def / 6.0, 0.0, 1.0)
            scoring = (
                tm.player.overall / 99.0 * 0.3
                + openness * 0.4
                + (1.0 - clamp(recv_dist / 30.0, 0.0, 1.0)) * 0.3
            )
            quality = lane.quality * 0.5 + scoring * 0.5
            qualities.append((tm.player_id, clamp(quality, 0.0, 1.0)))
        return qualities

    # -- Action execution -----------------------------------------------------

    def _execute_shot(
        self,
        handler: PlayerCourtState,
        home_on_offense: bool,
        catch_and_shoot: bool = False,
    ) -> None:
        """Execute a shot attempt using the 18-factor shot probability system."""
        gs = self.game_state
        player = handler.player
        is_home = home_on_offense
        attacking_right = self.court.attacking_right(home_on_offense)
        basket = self.court.basket_position(home_on_offense)
        dist = handler.position.distance_to(basket)
        zone = get_zone(handler.position, attacking_right)
        zone_info = get_zone_info(zone)
        is_three = zone_info.is_three

        base_rating = player.get_zone_rating(zone.name)
        def_dist = self.court.defender_distance(player.id, home_on_offense)
        contest_quality = clamp(1.0 - def_dist / 6.0, 0.0, 1.0)

        rim_protector = any(
            d.position.distance_to(basket) < 8.0
            and d.player.attributes.defense.block > 70
            for d in self.court.defensive_players(home_on_offense)
        )

        stats = self._player_stats(player.id, is_home)
        ctx = ShotContext(
            base_rating=base_rating,
            energy_pct=handler.energy.pct,
            is_open=def_dist > 4.0,
            is_catch_and_shoot=catch_and_shoot,
            is_off_dribble=not catch_and_shoot,
            hot_cold_modifier=self.confidence.get(player.id),
            shot_distance=dist,
            contest_distance=def_dist,
            contest_quality=contest_quality,
            rim_protector_present=rim_protector,
            deadeye_tier=player.badges.tier_value("deadeye"),
            catch_and_shoot_tier=player.badges.tier_value("catch_and_shoot"),
            hot_zone_hunter_tier=player.badges.tier_value("hot_zone_hunter"),
            corner_specialist_tier=player.badges.tier_value("corner_specialist"),
            volume_shooter_tier=player.badges.tier_value("volume_shooter"),
            is_clutch=gs.clock.is_clutch_time(),
            clutch_rating=player.attributes.mental.clutch,
            is_hot_zone=zone in (player.shooting_profile.hot_zones() or []),
            is_corner_three=zone in (Zone.THREE_LEFT_CORNER, Zone.THREE_RIGHT_CORNER),
            shot_attempts_this_game=stats.fga,
        )

        make_prob = calculate_shot_probability(ctx)
        # Momentum modifier
        if is_home:
            make_prob *= self.momentum.home_modifier()
        else:
            make_prob *= self.momentum.away_modifier()
        make_prob = clamp(make_prob, 0.02, 0.98)

        made = self._phys_rng.random() < make_prob
        points = 3 if is_three else 2

        # Consume ~1 second for the shot
        self._advance_clock(self._rng.uniform(0.5, 1.5))

        if made:
            stats.record_made_shot(is_three=is_three)
            gs.score.add_points(is_home, points, gs.clock.quarter)
            team_stats = self.home_stats if is_home else self.away_stats
            team_stats.points += points
            if zone_info.is_paint:
                team_stats.points_in_paint += points
            self.confidence.on_made_shot(player.id, was_three=is_three)
            if is_home:
                self.momentum.on_home_score(points)
            else:
                self.momentum.on_away_score(points)

            # Assist credit
            if self._last_passer_id and self._last_passer_id != player.id:
                passer_stats = self._player_stats(self._last_passer_id, is_home)
                passer_stats.assists += 1
                self.confidence.on_assist(self._last_passer_id)

            # And-one check
            foul_chance = contest_quality * 0.12 * (player.attributes.finishing.draw_foul / 99.0)
            is_and_one = self._phys_rng.random() < foul_chance

            if self.narration:
                ev = self.narration.narrate_made_shot(
                    shooter=player.full_name,
                    team=self._team_name(is_home),
                    points=points,
                    distance=dist,
                    zone=zone_info.name,
                    lead=gs.score.diff if is_home else -gs.score.diff,
                    is_and_one=is_and_one,
                )
                self._emit("made_shot", ev, {"player_id": player.id, "points": points})

            if is_and_one:
                self._free_throws(handler, 1, is_home)
        else:
            stats.record_missed_shot(is_three=is_three)
            self.confidence.on_missed_shot(player.id)

            # Block check
            blocked = False
            closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
            if closest_def and def_dist < 3.0:
                block_chance = closest_def.player.attributes.defense.block / 99.0 * 0.15
                if self._phys_rng.random() < block_chance:
                    blocked = True
                    blk_stats = self._player_stats(closest_def.player_id, not is_home)
                    blk_stats.blocks += 1
                    if self.narration:
                        ev = self.narration.narrate_block(
                            blocker=closest_def.player.full_name,
                            shooter=player.full_name,
                        )
                        self._emit("block", ev, {})

            if not blocked and self.narration:
                ev = self.narration.narrate_missed_shot(
                    shooter=player.full_name, distance=dist, zone=zone_info.name,
                )
                self._emit("missed_shot", ev, {"player_id": player.id})

            # Rebound
            self._resolve_rebound(home_on_offense)

    def _execute_drive(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> bool:
        """Execute a drive. Returns True if the possession resolved."""
        gs = self.game_state
        player = handler.player
        is_home = home_on_offense
        basket = self.court.basket_position(home_on_offense)

        # Move handler toward basket
        to_basket = (basket - handler.position).normalized()
        drive_dist = attribute_to_range(player.attributes.athleticism.speed, 5.0, 10.0)
        handler.position = Vec2(
            clamp(handler.position.x + to_basket.x * drive_dist, 0, COURT_LENGTH),
            clamp(handler.position.y + to_basket.y * drive_dist, 0, COURT_WIDTH),
        )
        handler.energy.drain(ENERGY_DRAIN_SPRINT * 5)

        closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
        def_dist = closest_def.position.distance_to(handler.position) if closest_def else 10.0

        # Consume drive time
        self._advance_clock(self._rng.uniform(1.5, 3.0))

        # Turnover chance
        to_chance = 0.07 + (1.0 - player.attributes.playmaking.ball_handle / 99.0) * 0.07
        if self._phys_rng.random() < to_chance:
            self._turnover(handler, is_home)
            return True

        # Foul chance
        contact = clamp(1.0 - def_dist / 5.0, 0.0, 0.6)
        if contact > 0.2 and self._phys_rng.random() < 0.20 * (
            player.attributes.finishing.draw_foul / 99.0
        ):
            self._foul_on_drive(handler, is_home)
            return True

        # Kick-out decision (30% chance if drive quality is low)
        new_dist = handler.position.distance_to(basket)
        if new_dist > 10.0 and self._phys_rng.random() < 0.3:
            return False  # Didn't resolve, will pass/shoot next action

        # At-rim shot
        finish_rating = max(
            player.attributes.finishing.layup,
            player.attributes.finishing.driving_dunk,
        )
        ctx = ShotContext(
            base_rating=finish_rating,
            energy_pct=handler.energy.pct,
            is_open=def_dist > 3.0,
            shot_distance=max(new_dist, 2.0),
            contest_distance=def_dist,
            contest_quality=clamp(1.0 - def_dist / 5.0, 0.0, 1.0),
            rim_protector_present=any(
                d.player.attributes.defense.block > 70
                for d in self.court.defensive_players(home_on_offense)
                if d.position.distance_to(basket) < 8.0
            ),
            is_clutch=gs.clock.is_clutch_time(),
            clutch_rating=player.attributes.mental.clutch,
        )
        make_prob = calculate_shot_probability(ctx)
        made = self._phys_rng.random() < make_prob
        stats = self._player_stats(player.id, is_home)

        if made:
            stats.record_made_shot(is_three=False)
            gs.score.add_points(is_home, 2, gs.clock.quarter)
            team_stats = self.home_stats if is_home else self.away_stats
            team_stats.points += 2
            team_stats.points_in_paint += 2
            self.confidence.on_made_shot(player.id)
            if is_home:
                self.momentum.on_home_score(2)
            else:
                self.momentum.on_away_score(2)

            is_dunk = (
                player.attributes.finishing.driving_dunk > 70
                and self._phys_rng.random() < 0.4
            )
            if self.narration:
                ev = self.narration.narrate_made_shot(
                    shooter=player.full_name,
                    team=self._team_name(is_home),
                    points=2, distance=new_dist, zone="paint",
                    lead=gs.score.diff if is_home else -gs.score.diff,
                    is_dunk=is_dunk,
                )
                self._emit("made_shot", ev, {"player_id": player.id, "points": 2})
            if is_dunk:
                self.momentum.on_dunk(is_home)
        else:
            stats.record_missed_shot(is_three=False)
            self.confidence.on_missed_shot(player.id)
            if self.narration:
                ev = self.narration.narrate_missed_shot(
                    shooter=player.full_name, distance=new_dist, zone="paint",
                )
                self._emit("missed_shot", ev, {"player_id": player.id})
            self._resolve_rebound(home_on_offense)

        return True

    def _execute_pass(
        self, handler: PlayerCourtState, target_id: int, home_on_offense: bool,
    ) -> bool:
        """Execute a pass. Returns True if stolen (possession ends)."""
        player = handler.player
        is_home = home_on_offense
        target = self.court.get_player_state(target_id)
        if target is None:
            return False

        defenders = self.court.defensive_players(home_on_offense)
        def_positions = [d.position for d in defenders]
        lane = analyze_passing_lane(
            passer_pos=handler.position,
            receiver_pos=target.position,
            defender_positions=def_positions,
        )

        # Adjust interception risk for passer skill
        pass_skill = (
            player.attributes.playmaking.pass_accuracy * 0.5
            + player.attributes.playmaking.pass_vision * 0.3
            + player.attributes.playmaking.pass_iq * 0.2
        ) / 99.0
        steal_chance = lane.interception_risk * (1.0 - pass_skill * 0.5)

        if self._phys_rng.random() < steal_chance:
            # Stolen
            stealer = min(
                defenders,
                key=lambda d: d.position.distance_to(
                    (handler.position + target.position) * 0.5,
                ),
            ) if defenders else None
            self._steal(handler, stealer, is_home)
            return True

        # Successful pass
        self._last_passer_id = handler.player_id
        self.court.ball.holder_id = target_id
        self.court.ball.status = BallStatus.HELD
        return False

    def _execute_post_up(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> None:
        """Execute a post-up move."""
        gs = self.game_state
        player = handler.player
        is_home = home_on_offense
        basket = self.court.basket_position(home_on_offense)

        to_basket = (basket - handler.position).normalized()
        handler.position = Vec2(
            clamp(handler.position.x + to_basket.x * 3.0, 0, COURT_LENGTH),
            clamp(handler.position.y + to_basket.y * 3.0, 0, COURT_WIDTH),
        )
        handler.energy.drain(ENERGY_DRAIN_SPRINT * 3)
        self._advance_clock(self._rng.uniform(2.0, 4.0))

        post_rating = max(
            player.attributes.finishing.post_hook,
            player.attributes.finishing.post_fadeaway,
            player.attributes.finishing.post_moves,
        )
        def_dist = self.court.defender_distance(player.id, home_on_offense)
        dist = handler.position.distance_to(basket)

        ctx = ShotContext(
            base_rating=post_rating,
            energy_pct=handler.energy.pct,
            shot_distance=max(dist, 3.0),
            contest_distance=def_dist,
            contest_quality=clamp(1.0 - def_dist / 5.0, 0.0, 1.0),
            is_off_dribble=True,
            is_clutch=gs.clock.is_clutch_time(),
            clutch_rating=player.attributes.mental.clutch,
        )
        make_prob = calculate_shot_probability(ctx)
        made = self._phys_rng.random() < make_prob
        stats = self._player_stats(player.id, is_home)

        if made:
            stats.record_made_shot(is_three=False)
            gs.score.add_points(is_home, 2, gs.clock.quarter)
            team_stats = self.home_stats if is_home else self.away_stats
            team_stats.points += 2
            team_stats.points_in_paint += 2
            self.confidence.on_made_shot(player.id)
            if is_home:
                self.momentum.on_home_score(2)
            else:
                self.momentum.on_away_score(2)
            if self.narration:
                ev = self.narration.narrate_made_shot(
                    shooter=player.full_name,
                    team=self._team_name(is_home),
                    points=2, distance=dist, zone="post",
                    lead=gs.score.diff if is_home else -gs.score.diff,
                )
                self._emit("made_shot", ev, {"player_id": player.id, "points": 2})
        else:
            stats.record_missed_shot(is_three=False)
            self.confidence.on_missed_shot(player.id)
            if self.narration:
                ev = self.narration.narrate_missed_shot(
                    shooter=player.full_name, distance=dist, zone="post",
                )
                self._emit("missed_shot", ev, {"player_id": player.id})
            self._resolve_rebound(home_on_offense)

    # -- Secondary actions ----------------------------------------------------

    def _resolve_rebound(self, home_on_offense: bool) -> None:
        offense = self.court.offensive_players(home_on_offense)
        defense = self.court.defensive_players(home_on_offense)
        basket = self.court.basket_position(home_on_offense)
        candidates: list[tuple[PlayerCourtState, float, bool]] = []

        for pcs in offense:
            dist = pcs.position.distance_to(basket)
            if dist > 20.0:
                continue
            reb = pcs.player.attributes.rebounding.offensive_rebound
            prox = max(0, 1.0 - dist / 15.0)
            chance = (reb / 99.0) * 0.5 + prox * 0.3 + pcs.player.tendencies.crash_boards * 0.2
            candidates.append((pcs, chance * 0.30, True))

        for pcs in defense:
            dist = pcs.position.distance_to(basket)
            if dist > 20.0:
                continue
            reb = pcs.player.attributes.rebounding.defensive_rebound
            prox = max(0, 1.0 - dist / 15.0)
            chance = (reb / 99.0) * 0.5 + prox * 0.3 + (
                pcs.player.attributes.rebounding.box_out / 99.0 * 0.2
            )
            candidates.append((pcs, chance, False))

        if not candidates:
            return

        total = sum(c[1] for c in candidates)
        if total <= 0:
            return

        roll = self._phys_rng.random() * total
        cumulative = 0.0
        rebounder = candidates[0]
        for cand in candidates:
            cumulative += cand[1]
            if roll <= cumulative:
                rebounder = cand
                break

        pcs, _, is_oreb = rebounder
        stats = self._player_stats(pcs.player_id, self._is_home_player(pcs))

        if is_oreb:
            stats.offensive_rebounds += 1
            # Continue possession: don't flip
            self.court.ball.holder_id = pcs.player_id
            self.court.ball.status = BallStatus.HELD
            # Offensive rebound resets shot clock to 14
            self.game_state.clock.shot_clock = min(14.0, self.game_state.clock.game_clock)
        else:
            stats.defensive_rebounds += 1
            # Defensive rebound -- possession will flip after this shot attempt

    def _turnover(self, handler: PlayerCourtState, is_home: bool) -> None:
        stats = self._player_stats(handler.player_id, is_home)
        stats.turnovers += 1
        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.turnovers += 1
        self.confidence.on_turnover(handler.player_id)
        self.momentum.on_turnover(is_home)
        if self.narration:
            ev = self.narration.narrate_turnover(
                player=handler.player.full_name, team=self._team_name(is_home),
            )
            self._emit("turnover", ev, {"player_id": handler.player_id})

    def _steal(
        self, handler: PlayerCourtState, stealer: PlayerCourtState | None, is_home: bool,
    ) -> None:
        stats = self._player_stats(handler.player_id, is_home)
        stats.turnovers += 1
        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.turnovers += 1
        self.confidence.on_turnover(handler.player_id)

        stealer_name = "Defense"
        if stealer:
            s_stats = self._player_stats(stealer.player_id, not is_home)
            s_stats.steals += 1
            stealer_name = stealer.player.full_name
            self.momentum.on_steal(not is_home)

        if self.narration:
            ev = self.narration.narrate_turnover(
                player=handler.player.full_name,
                passer=handler.player.full_name,
                stealer=stealer_name,
                team=self._team_name(is_home),
            )
            self._emit("steal", ev, {})

    def _foul_on_drive(self, handler: PlayerCourtState, is_home: bool) -> None:
        gs = self.game_state
        closest = self.court.closest_defender_to(handler.position, is_home)
        if closest:
            d_stats = self._player_stats(closest.player_id, not is_home)
            d_stats.personal_fouls += 1
            closest.fouls += 1
            if is_home:
                gs.away_team_fouls += 1
            else:
                gs.home_team_fouls += 1
            if self.narration:
                ev = self.narration.narrate_foul(
                    fouler=closest.player.full_name,
                    player=handler.player.full_name,
                    team_fouls=gs.away_team_fouls if is_home else gs.home_team_fouls,
                    fts=2,
                )
                self._emit("foul", ev, {})
        self._free_throws(handler, 2, is_home)

    def _free_throws(self, shooter: PlayerCourtState, count: int, is_home: bool) -> None:
        gs = self.game_state
        player = shooter.player
        stats = self._player_stats(player.id, is_home)
        ft_rating = player.attributes.shooting.free_throw
        energy_mod = 0.85 + shooter.energy.pct * 0.15

        for _ in range(count):
            prob = clamp(ft_rating / 100.0 * energy_mod, 0.1, 0.98)
            made = self._phys_rng.random() < prob
            if made:
                stats.record_made_ft()
                gs.score.add_points(is_home, 1, gs.clock.quarter)
                team_stats = self.home_stats if is_home else self.away_stats
                team_stats.points += 1
            else:
                stats.record_missed_ft()
            if self.narration:
                ev = self.narration.narrate_free_throw(shooter=player.full_name, made=made)
                self._emit("free_throw", ev, {"made": made})

    # -- Energy ---------------------------------------------------------------

    def _drain_energy_for_time(self, seconds: float) -> None:
        ticks = int(seconds / TICK_DURATION)
        for pcs in self.court.all_on_court():
            pcs.energy.drain(ENERGY_DRAIN_JOG * ticks)
        for pcs in self.court.home_bench + self.court.away_bench:
            pcs.energy.recover(ENERGY_RECOVERY_BENCH * ticks)
        # Track minutes
        for pcs in self.court.all_on_court():
            pcs.minutes_played += seconds / 60.0

    # -- Coach AI -------------------------------------------------------------

    def _check_coach_decisions(self, home_on_offense: bool) -> None:
        gs = self.game_state
        for is_home in [True, False]:
            on_court = self.court.home_on_court if is_home else self.court.away_on_court
            bench = self.court.home_bench if is_home else self.court.away_bench
            if not bench:
                continue
            for pcs in list(on_court):
                urgency = evaluate_substitution_need(
                    player_energy_pct=pcs.energy.pct,
                    player_fouls=pcs.fouls,
                    minutes_played=pcs.minutes_played,
                    quarter=gs.clock.quarter,
                    is_starter=pcs.player.overall >= 70,
                    is_closing_lineup=gs.clock.quarter >= 4 and gs.clock.game_clock < 300,
                )
                if urgency > 0.5 and bench:
                    best_sub = max(bench, key=lambda b: b.player.overall)
                    self._substitute(pcs, best_sub, is_home)
                    break

        # Timeout check
        is_def_home = not home_on_offense
        timeouts = gs.home_timeouts if is_def_home else gs.away_timeouts
        if should_call_timeout(
            opponent_run=self._opponent_run,
            own_turnovers_last_3=sum(1 for x in self._own_turnovers_recent[-3:] if x),
            timeouts_remaining=timeouts,
            is_clutch=gs.clock.is_clutch_time(),
            quarter=gs.clock.quarter,
        ):
            self._call_timeout(is_def_home)

    def _substitute(
        self, out_pcs: PlayerCourtState, in_pcs: PlayerCourtState, is_home: bool,
    ) -> None:
        on_court = self.court.home_on_court if is_home else self.court.away_on_court
        bench = self.court.home_bench if is_home else self.court.away_bench
        if out_pcs in on_court and in_pcs in bench:
            in_pcs.defensive_assignment_id = out_pcs.defensive_assignment_id
            in_pcs.position = out_pcs.position
            in_pcs.is_on_court = True
            out_pcs.is_on_court = False
            on_court.remove(out_pcs)
            bench.remove(in_pcs)
            on_court.append(in_pcs)
            bench.append(out_pcs)
            if self.court.ball.holder_id == out_pcs.player_id:
                self.court.ball.holder_id = in_pcs.player_id

    def _call_timeout(self, is_home: bool) -> None:
        gs = self.game_state
        if is_home:
            gs.home_timeouts -= 1
        else:
            gs.away_timeouts -= 1
        self.momentum.on_timeout()
        on_court = self.court.home_on_court if is_home else self.court.away_on_court
        for pcs in on_court:
            pcs.energy.recover(2.0)
        if self.narration:
            remaining = gs.home_timeouts if is_home else gs.away_timeouts
            ev = self.narration.narrate_timeout(
                team=self._team_name(is_home), remaining=remaining,
            )
            self._emit("timeout", ev, {})

    # -- Helpers --------------------------------------------------------------

    def _player_stats(self, player_id: int, is_home: bool):
        tracker = self.home_stats if is_home else self.away_stats
        return tracker.get_player(player_id)

    def _is_home_player(self, pcs: PlayerCourtState) -> bool:
        return any(
            h.player_id == pcs.player_id
            for h in self.court.home_on_court + self.court.home_bench
        )

    def _team_name(self, is_home: bool) -> str:
        return self.home_team.full_name if is_home else self.away_team.full_name

    def _emit(self, event_type: str, narration: NarrationEvent, data: dict) -> None:
        self._events.append(SimEvent(narration=narration, event_type=event_type, data=data))
