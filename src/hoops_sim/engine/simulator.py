"""GameSimulator: the real basketball simulation engine.

Owns the full game loop and wires together all subsystems:
- GameState / GameClock (clock management)
- CourtState (player positions, ball state)
- ActionStateMachine (per-player micro-action FSMs)
- PlayerKinematics (physics-based movement)
- Dribble moves, pass types, screen mechanics
- Defensive AI, help rotations, closeouts
- Shot probability with context from preceding actions
- Energy/Fatigue system
- Coach AI (substitutions, timeouts, play calling)
- Narration engine
- Momentum/Confidence tracking
- Contact detection and foul adjudication
- Situational basketball and clock management

The simulation runs at **tick-level resolution** (0.1s per tick). Each
possession unfolds as a sequence of micro-actions: dribble moves, screens,
passes, cuts, drives, and shots -- all consuming real time and space.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.actions.dribble import (
    DRIBBLE_MOVES,
    DribbleMoveType,
    resolve_dribble_move,
)
from hoops_sim.actions.finishing import select_finish_type
from hoops_sim.actions.passing import PassType, resolve_pass
from hoops_sim.actions.screen import ScreenType, evaluate_screen
from hoops_sim.ai.coach_brain import (
    evaluate_substitution_need,
    should_call_timeout,
)
from hoops_sim.ai.player_brain import ActionOption, evaluate_ball_handler_options
from hoops_sim.court.driving_lanes import analyze_driving_lane
from hoops_sim.court.model import get_basket_position
from hoops_sim.court.passing_lanes import analyze_passing_lane
from hoops_sim.court.zones import Zone, get_zone, get_zone_info
from hoops_sim.defense.pnr_coverage import PnRCoverageType, evaluate_pnr_coverage
from hoops_sim.engine.action_fsm import (
    ACTION_DURATIONS,
    ActionStateMachine,
    BallHandlerState,
    DefenderState,
    MovementIntent,
    OffBallOffenseState,
    PossessionEvent,
    PossessionEventType,
)
from hoops_sim.engine.court_state import (
    BallStatus,
    CourtState,
    PlayerCourtState,
    create_initial_positions,
)
from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.possession import PossessionState
from hoops_sim.engine.situational import evaluate_situation
from hoops_sim.engine.transition import evaluate_transition
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.models.team import Team
from hoops_sim.narration.broadcast_mixer import BroadcastLine, BroadcastMixer
from hoops_sim.narration.color_commentary import ColorCommentaryNarrator
from hoops_sim.narration.engine import NarrationEngine, NarrationEvent
from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    MilestoneEvent,
    MomentumEvent,
    MomentumKind,
    PassEvent,
    PossessionStartEvent,
    QuarterBoundaryEvent,
    QuarterEventKind,
    ReboundEvent,
    ScreenEvent,
    ShotResultEvent,
    SubstitutionEvent,
    TimeoutEvent,
    TurnoverEvent,
)
from hoops_sim.narration.narrative_arc import NarrativeArcTracker
from hoops_sim.narration.play_by_play import PlayByPlayNarrator
from hoops_sim.narration.possession_narrator import PossessionNarrator
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.physics.kinematics import MovementType
from hoops_sim.physics.vec import Vec2
from hoops_sim.plays.playbook import (
    FAST_BREAK,
    ISOLATION,
    MOTION_OFFENSE,
    PICK_AND_ROLL,
    POST_UP,
    PlayDefinition,
)
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

# Maximum ticks per possession to prevent infinite loops
MAX_TICKS_PER_POSSESSION = 300  # 30 seconds


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

    Simulates at the tick level: each possession unfolds as a sequence
    of micro-actions (dribble moves, screens, passes, drives, shots)
    that consume real time and real space on the court.
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

        # Initialize kinematics and FSMs for all on-court players
        for pcs in self.court.all_on_court():
            pcs.init_kinematics()

        # Subsystems
        self.narration = NarrationEngine(self._rng) if narrate else None
        self.momentum = MomentumTracker()
        self.confidence = ConfidenceTracker()

        # Broadcast-quality narration system
        self.broadcast_stats: LiveStatTracker | None = None
        self.broadcast_mixer: BroadcastMixer | None = None
        if narrate:
            self.broadcast_stats = LiveStatTracker(
                home_team=home_team.full_name,
                away_team=away_team.full_name,
            )
            arc_tracker = NarrativeArcTracker(
                home_team=home_team.full_name,
                away_team=away_team.full_name,
                stat_tracker=self.broadcast_stats,
            )
            pbp = PlayByPlayNarrator(self._rng, self.broadcast_stats)
            color = ColorCommentaryNarrator(self._rng, self.broadcast_stats, arc_tracker)
            possession_narrator = PossessionNarrator(pbp, color)
            self.broadcast_mixer = BroadcastMixer(
                possession_narrator=possession_narrator,
                stat_tracker=self.broadcast_stats,
                arc_tracker=arc_tracker,
            )

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

        # Micro-action tracking
        self._possession_events: list[PossessionEvent] = []
        self._current_play: PlayDefinition | None = None
        self._pending_screener_id: int | None = None
        self._is_transition: bool = False

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
        """Simulate a single possession using the micro-action tick loop.

        This is the core of the overhaul: instead of random time + action cycles,
        we process 10 player FSMs every tick (0.1s) until the possession ends.
        """
        gs = self.game_state

        if self._game_over:
            return

        self._total_possessions += 1
        home_on_offense = self._off_team_id == self.home_team.id
        is_home = home_on_offense

        # Set up the possession
        self._setup_possession(home_on_offense)

        # Start broadcast possession tracking
        if self.broadcast_mixer is not None:
            self.broadcast_mixer.start_possession(gs.clock.quarter, gs.clock.game_clock)

        # Evaluate situation for tactical modifiers
        situation_type, sit_mods = evaluate_situation(
            game_clock=gs.clock.game_clock,
            shot_clock=gs.clock.shot_clock,
            quarter=gs.clock.quarter,
            score_diff=gs.score.diff if is_home else -gs.score.diff,
            is_home=is_home,
        )

        # Phase 1: Bring the ball up court
        # Transition possessions are faster (1-3 seconds vs 3-6 seconds)
        is_transition = self._is_transition
        self._is_transition = False  # Reset for next possession
        if is_transition:
            bring_up_ticks = self._rng.randint(10, 30)
        else:
            bring_up_ticks = self._rng.randint(30, 60)
        handler = self._get_ball_handler(home_on_offense)
        handler_name = handler.player.full_name if handler else ""
        self._broadcast_event(BallAdvanceEvent(
            ball_handler_name=handler_name,
            is_transition=is_transition,
            seconds_to_advance=bring_up_ticks * TICK_DURATION,
            **self._make_base_fields(),
        ))
        self._advance_clock(bring_up_ticks * TICK_DURATION)
        self._drain_energy_for_ticks(bring_up_ticks)
        if self._check_quarter_end():
            self._flush_broadcast_lines()
            return

        # Phase 2: Coach selects play (fast break in transition)
        if is_transition:
            self._current_play = FAST_BREAK
        else:
            self._current_play = self._select_play(home_on_offense, situation_type)
        self._assign_play_roles(home_on_offense)

        # Emit possession start event
        self._broadcast_event(PossessionStartEvent(
            ball_handler_name=handler_name,
            ball_handler_id=handler.player_id if handler else 0,
            offensive_team=self._team_name(is_home),
            defensive_team=self._team_name(not is_home),
            play_call=self._current_play.name if self._current_play else "",
            **self._make_base_fields(),
        ))

        # Phase 3: Micro-action tick loop
        self._possession_events = []
        possession_resolved = False
        ticks_elapsed = 0

        while not possession_resolved and ticks_elapsed < MAX_TICKS_PER_POSSESSION:
            ticks_elapsed += 1

            # Advance game clock
            self._advance_clock(TICK_DURATION)
            if self._check_quarter_end():
                return

            # Check shot clock
            if gs.clock.shot_clock <= 0.0:
                self._shot_clock_violation(home_on_offense)
                self._end_possession_and_flip()
                return

            # Process all 10 player FSMs
            handler = self._get_ball_handler(home_on_offense)
            if handler is None:
                break

            # Tick all FSMs and update positions
            self._tick_all_players(home_on_offense)

            # Ball handler AI decision (when their action completes or is interruptible)
            if handler.fsm.can_interrupt:
                possession_resolved = self._process_ball_handler_tick(
                    handler, home_on_offense, ticks_elapsed, sit_mods,
                )

            # Drain energy for this tick
            self._drain_energy_for_ticks(1)

        # If we exhausted ticks without resolving, force a shot
        if not possession_resolved:
            handler = self._get_ball_handler(home_on_offense)
            if handler:
                self._execute_shot(handler, home_on_offense, catch_and_shoot=False)
            self._end_possession_and_flip()

    def _process_ball_handler_tick(
        self,
        handler: PlayerCourtState,
        home_on_offense: bool,
        ticks_elapsed: int,
        sit_mods: object,
    ) -> bool:
        """Process a ball handler's decision for this tick.

        Returns True if the possession is resolved (shot taken, turnover, etc.).
        """
        gs = self.game_state
        player = handler.player
        basket = self.court.basket_position(home_on_offense)

        # Get current context
        shot_quality = self._eval_shot_quality(handler, home_on_offense)
        drive_quality = self._eval_drive_quality(handler, home_on_offense)
        pass_qualities = self._eval_pass_qualities(handler, home_on_offense)
        post_quality = 0.0
        if (handler.position.distance_to(basket) < 15.0
                and player.attributes.finishing.post_moves > 60):
            post_quality = player.attributes.finishing.post_moves / 100.0 * 0.7

        shot_clock_pct = gs.clock.shot_clock / 24.0

        # Run player AI
        action = evaluate_ball_handler_options(
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

        # Early possession: bias toward passing to move the ball
        if ticks_elapsed < 30 and action.action == "shoot" and shot_clock_pct > 0.5:
            if pass_qualities and self._rng.random() < 0.50:
                best_pass = max(pass_qualities, key=lambda pq: pq[1])
                action = ActionOption("pass", 0.5, target_id=best_pass[0])

        # Execute the chosen action
        if action.action == "shoot":
            # Execute a dribble move before shooting if defender is close
            def_dist = self.court.defender_distance(player.id, home_on_offense)
            if def_dist < 5.0 and self._rng.random() < 0.4:
                self._execute_dribble_move(handler, home_on_offense)
            self._execute_shot(handler, home_on_offense, catch_and_shoot=False)
            self._end_possession_and_flip()
            return True

        elif action.action == "drive":
            # Execute a dribble move to create space before driving
            if self._rng.random() < 0.6:
                self._execute_dribble_move(handler, home_on_offense)
            resolved = self._execute_drive(handler, home_on_offense)
            if resolved:
                self._end_possession_and_flip()
                return True
            # Drive kicked out: transition to pass
            handler.fsm.transition_to(
                BallHandlerState.DRIBBLING_IN_PLACE,
                ticks=self._rng.randint(5, 15),
                target=handler.position,
                intent=MovementIntent.STAND,
            )
            return False

        elif action.action == "pass" and action.target_id is not None:
            stolen = self._execute_pass(handler, action.target_id, home_on_offense)
            if stolen:
                self._end_possession_and_flip()
                return True
            # Successful pass: receiver decides next
            handler.fsm.transition_to(
                OffBallOffenseState.RELOCATING,
                ticks=self._rng.randint(10, 20),
                target=self._find_spot_up_position(handler, home_on_offense),
                intent=MovementIntent.JOG,
            )
            return False

        elif action.action == "post_up":
            self._execute_post_up(handler, home_on_offense)
            self._end_possession_and_flip()
            return True

        else:
            # Hold: try using a screen if one is pending, otherwise dribble
            if self._pending_screener_id is not None:
                screener_pcs = self.court.get_player_state(self._pending_screener_id)
                if screener_pcs and screener_pcs.fsm.is_complete:
                    self._execute_screen(handler, home_on_offense)
                    return False
            if self._rng.random() < 0.3:
                self._execute_dribble_move(handler, home_on_offense)
            handler.fsm.transition_to(
                BallHandlerState.DRIBBLING_IN_PLACE,
                ticks=self._rng.randint(5, 20),
                target=handler.position,
                intent=MovementIntent.STAND,
            )
            return False

    def _tick_all_players(self, home_on_offense: bool) -> None:
        """Advance all 10 player FSMs by one tick and update positions."""
        for pcs in self.court.all_on_court():
            # Tick the FSM
            pcs.fsm.tick()

            # Update position via kinematics if available
            if pcs.kinematics is not None:
                movement_type = self._intent_to_movement_type(pcs.fsm.movement_intent)
                pcs.kinematics.update(
                    dt=TICK_DURATION,
                    target_position=pcs.fsm.movement_target,
                    movement_type=movement_type,
                )
                # Sync position from kinematics
                pcs.position = Vec2(
                    clamp(pcs.kinematics.position.x, 0, COURT_LENGTH),
                    clamp(pcs.kinematics.position.y, 0, COURT_WIDTH),
                )

        # Update off-ball players' FSMs when their action completes
        offense = self.court.offensive_players(home_on_offense)
        defense = self.court.defensive_players(home_on_offense)
        basket = self.court.basket_position(home_on_offense)
        ball_handler = self.court.ball_handler()

        for pcs in offense:
            if ball_handler and pcs.player_id == ball_handler.player_id:
                continue  # Ball handler is handled separately
            if pcs.fsm.is_complete:
                self._decide_off_ball_action(pcs, home_on_offense, basket)

        for pcs in defense:
            if pcs.fsm.is_complete:
                self._decide_defensive_action(pcs, home_on_offense, basket)

    def _decide_off_ball_action(
        self, pcs: PlayerCourtState, home_on_offense: bool, basket: Vec2,
    ) -> None:
        """Decide what an off-ball offensive player does next."""
        player = pcs.player
        roll = self._rng.random()

        # Check defender position for backdoor cut opportunity
        def_dist = self.court.defender_distance(pcs.player_id, home_on_offense)
        defender_overplaying = def_dist < 2.5

        # Backdoor cut when defender overplays passing lane
        if defender_overplaying and player.attributes.athleticism.speed > 65 and roll < 0.35:
            pcs.fsm.transition_to(
                OffBallOffenseState.CUTTING,
                ticks=self._rng.randint(6, 12),
                target=basket,
                intent=MovementIntent.SPRINT,
            )
            return

        # Set off-ball screen (pin-down, flare) for teammates
        if (player.attributes.athleticism.strength > 65
                and player.body.weight_lbs > 200
                and roll < 0.20):
            # Find a shooter teammate to screen for
            ball_handler = self.court.ball_handler()
            teammates = [
                t for t in self.court.offensive_players(home_on_offense)
                if t.player_id != pcs.player_id
                and (ball_handler is None or t.player_id != ball_handler.player_id)
                and t.player.attributes.shooting.three_point > 70
            ]
            if teammates:
                screen_target = teammates[0].position
                pcs.fsm.transition_to(
                    OffBallOffenseState.SETTING_SCREEN,
                    ticks=self._rng.randint(10, 18),
                    target=screen_target,
                    intent=MovementIntent.JOG,
                )
                return

        # Crash offensive glass based on tendencies
        if (player.tendencies.crash_boards > 0.5
                and player.attributes.rebounding.offensive_rebound > 60
                and roll < 0.25):
            pcs.fsm.transition_to(
                OffBallOffenseState.CRASHING_BOARDS,
                ticks=self._rng.randint(10, 20),
                target=basket,
                intent=MovementIntent.SPRINT,
            )
            return

        # Spot up at the three-point line if a shooter
        if player.attributes.shooting.three_point > 65:
            target = self._find_spot_up_position(pcs, home_on_offense)
            pcs.fsm.transition_to(
                OffBallOffenseState.SPOTTING_UP,
                ticks=self._rng.randint(15, 40),
                target=target,
                intent=MovementIntent.JOG,
            )
        # Cut if a good finisher
        elif player.attributes.finishing.layup > 70 and roll < 0.30:
            pcs.fsm.transition_to(
                OffBallOffenseState.CUTTING,
                ticks=self._rng.randint(8, 15),
                target=basket,
                intent=MovementIntent.SPRINT,
            )
        else:
            # Relocate to maintain spacing
            target = self._find_spot_up_position(pcs, home_on_offense)
            pcs.fsm.transition_to(
                OffBallOffenseState.RELOCATING,
                ticks=self._rng.randint(10, 25),
                target=target,
                intent=MovementIntent.JOG,
            )

    def _decide_defensive_action(
        self, pcs: PlayerCourtState, home_on_offense: bool, basket: Vec2,
    ) -> None:
        """Decide what a defensive player does next."""
        # Find their assignment
        assignment = None
        if pcs.defensive_assignment_id is not None:
            assignment = self.court.get_player_state(pcs.defensive_assignment_id)

        ball_handler = self.court.ball_handler()

        if assignment is None:
            # Guard the ball handler area
            if ball_handler:
                target = ball_handler.position + (basket - ball_handler.position).normalized() * 5
            else:
                target = basket
            pcs.fsm.transition_to(
                DefenderState.GUARDING_ON_BALL,
                ticks=self._rng.randint(5, 15),
                target=target,
                intent=MovementIntent.JOG,
            )
            return

        # If assignment has the ball, guard on-ball
        if ball_handler and assignment.player_id == ball_handler.player_id:
            to_basket = (basket - assignment.position).normalized()
            guard_pos = assignment.position + to_basket * 3.0
            pcs.fsm.transition_to(
                DefenderState.GUARDING_ON_BALL,
                ticks=self._rng.randint(3, 10),
                target=guard_pos,
                intent=MovementIntent.LATERAL,
            )
        else:
            # Off-ball: deny position between assignment and basket
            to_basket = (basket - assignment.position).normalized()
            deny_pos = assignment.position + to_basket * 3.0
            if ball_handler:
                to_ball = (ball_handler.position - assignment.position).normalized()
                deny_pos = assignment.position + to_basket * 2.5 + to_ball * 1.0
            pcs.fsm.transition_to(
                DefenderState.DENYING_PASS,
                ticks=self._rng.randint(5, 20),
                target=deny_pos,
                intent=MovementIntent.JOG,
            )

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

        # Initialize FSMs for all players
        self._init_player_fsms(home_on_offense)

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
            handler.fsm.transition_to(
                BallHandlerState.BRINGING_BALL_UP,
                ticks=self._rng.randint(20, 40),
                target=self.court.basket_position(home_on_offense),
                intent=MovementIntent.JOG,
            )

        # Coach AI between possessions
        self._check_coach_decisions(home_on_offense)
        self.confidence.decay_all()
        self.momentum.decay()

    def _init_player_fsms(self, home_on_offense: bool) -> None:
        """Set initial FSM states for all on-court players."""
        basket = self.court.basket_position(home_on_offense)
        offense = self.court.offensive_players(home_on_offense)
        defense = self.court.defensive_players(home_on_offense)

        for pcs in offense:
            if self.court.ball.holder_id == pcs.player_id:
                continue  # Ball handler FSM set separately
            pcs.fsm.transition_to(
                OffBallOffenseState.SPOTTING_UP,
                ticks=self._rng.randint(15, 30),
                target=pcs.position,
                intent=MovementIntent.JOG,
            )
            pcs.fsm.is_offense = True

        for pcs in defense:
            assignment = None
            if pcs.defensive_assignment_id is not None:
                assignment = self.court.get_player_state(pcs.defensive_assignment_id)
            target = pcs.position
            if assignment:
                to_basket = (basket - assignment.position).normalized()
                target = assignment.position + to_basket * 3.0
            pcs.fsm.transition_to(
                DefenderState.DENYING_PASS,
                ticks=self._rng.randint(10, 30),
                target=target,
                intent=MovementIntent.JOG,
            )
            pcs.fsm.is_offense = False

    def _select_play(self, home_on_offense: bool, situation_type: object) -> PlayDefinition:
        """Coach selects a play based on situation and personnel."""
        plays = [PICK_AND_ROLL, ISOLATION, MOTION_OFFENSE, POST_UP, FAST_BREAK]
        weights = [0.30, 0.15, 0.25, 0.15, 0.15]

        # Adjust weights based on personnel
        offense = self.court.offensive_players(home_on_offense)
        if offense:
            best_player = max(offense, key=lambda p: p.player.overall)
            # Star player -> more isolation
            if best_player.player.overall > 85:
                weights[1] *= 1.5
            # Good passer -> more PnR and motion
            if best_player.player.attributes.playmaking.pass_vision > 75:
                weights[0] *= 1.3
                weights[2] *= 1.2
            # Post player -> more post ups
            if best_player.player.attributes.finishing.post_moves > 70:
                weights[3] *= 1.5

        return self._rng.choices(plays, weights=weights, k=1)[0]

    def _assign_play_roles(self, home_on_offense: bool) -> None:
        """Assign play roles to players based on the selected play."""
        if self._current_play is None:
            return

        offense = self.court.offensive_players(home_on_offense)
        ball_handler = self.court.ball_handler()
        basket = self.court.basket_position(home_on_offense)
        if not offense or ball_handler is None:
            return

        # Non-handler players
        off_ball = [p for p in offense if p.player_id != ball_handler.player_id]
        if not off_ball:
            return

        play_name = self._current_play.name

        if play_name == PICK_AND_ROLL.name and off_ball:
            # Pick best screener: heaviest / strongest player
            screener = max(
                off_ball,
                key=lambda p: (
                    p.player.attributes.athleticism.strength
                    + p.player.body.weight_lbs
                ),
            )
            # Move screener toward ball handler to set screen
            screen_pos = ball_handler.position + (basket - ball_handler.position).normalized() * 3.0
            screener.fsm.transition_to(
                OffBallOffenseState.SETTING_SCREEN,
                ticks=self._rng.randint(10, 20),
                target=screen_pos,
                intent=MovementIntent.JOG,
            )
            self._pending_screener_id = screener.player_id

        elif play_name == ISOLATION.name:
            # Clear out: all off-ball players space to the perimeter
            for pcs in off_ball:
                target = self._find_spot_up_position(pcs, home_on_offense)
                pcs.fsm.transition_to(
                    OffBallOffenseState.SPOTTING_UP,
                    ticks=self._rng.randint(15, 30),
                    target=target,
                    intent=MovementIntent.JOG,
                )
            self._pending_screener_id = None

        elif play_name == MOTION_OFFENSE.name:
            # Motion: one player cuts, one screens away, rest space
            if len(off_ball) >= 2:
                cutter = off_ball[0]
                screener = off_ball[1]
                cutter.fsm.transition_to(
                    OffBallOffenseState.CUTTING,
                    ticks=self._rng.randint(8, 15),
                    target=basket,
                    intent=MovementIntent.SPRINT,
                )
                # Screen away from the ball
                screen_target = cutter.position + (basket - cutter.position).normalized() * 5.0
                screener.fsm.transition_to(
                    OffBallOffenseState.SETTING_SCREEN,
                    ticks=self._rng.randint(10, 18),
                    target=screen_target,
                    intent=MovementIntent.JOG,
                )
            for pcs in off_ball[2:]:
                target = self._find_spot_up_position(pcs, home_on_offense)
                pcs.fsm.transition_to(
                    OffBallOffenseState.SPOTTING_UP,
                    ticks=self._rng.randint(15, 30),
                    target=target,
                    intent=MovementIntent.JOG,
                )
            self._pending_screener_id = None

        elif play_name == POST_UP.name and off_ball:
            # Find best post player
            post_player = max(
                off_ball,
                key=lambda p: p.player.attributes.finishing.post_moves,
            )
            post_pos = basket + Vec2(0, self._rng.choice([-5.0, 5.0]))
            post_player.fsm.transition_to(
                OffBallOffenseState.CUTTING,
                ticks=self._rng.randint(10, 20),
                target=post_pos,
                intent=MovementIntent.JOG,
            )
            for pcs in off_ball:
                if pcs.player_id != post_player.player_id:
                    target = self._find_spot_up_position(pcs, home_on_offense)
                    pcs.fsm.transition_to(
                        OffBallOffenseState.SPOTTING_UP,
                        ticks=self._rng.randint(15, 30),
                        target=target,
                        intent=MovementIntent.JOG,
                    )
            self._pending_screener_id = None
        else:
            self._pending_screener_id = None

    def _end_possession_and_flip(self) -> None:
        """Flip possession to the other team."""
        # End broadcast possession and capture output
        self._flush_broadcast_lines()
        old_off = self._off_team_id
        old_def = self._def_team_id
        self._off_team_id = old_def
        self._def_team_id = old_off

    def _flush_broadcast_lines(self) -> None:
        """Capture broadcast mixer output and convert to SimEvents."""
        if self.broadcast_mixer is None:
            return
        lines = self.broadcast_mixer.end_possession()
        for line in lines:
            narration = NarrationEvent(text=line.text)
            self._emit("broadcast", narration, {
                "voice": line.voice,
                "intensity": line.intensity,
            })

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

        q_kind = QuarterEventKind.HALFTIME if self._quarter == 3 else QuarterEventKind.QUARTER_END
        base = self._make_base_fields()
        base["quarter"] = self._quarter - 1  # Override with ended quarter
        self._broadcast_event(QuarterBoundaryEvent(
            kind=q_kind,
            home_team=self.home_team.full_name,
            away_team=self.away_team.full_name,
            **base,
        ))
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
                # Sync kinematics position
                if pcs.kinematics is not None:
                    pcs.kinematics.position = pcs.position.copy()
                    pcs.kinematics.velocity = Vec2.zero()

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
                if dcs.kinematics is not None:
                    dcs.kinematics.position = dcs.position.copy()
                    dcs.kinematics.velocity = Vec2.zero()

    def _find_spot_up_position(
        self, pcs: PlayerCourtState, home_on_offense: bool,
    ) -> Vec2:
        """Find a good spot-up position for spacing."""
        basket = self.court.basket_position(home_on_offense)
        direction = pcs.position - basket
        if direction.magnitude() < 0.1:
            direction = Vec2(1.0, 0.0)
        direction = direction.normalized()

        if pcs.player.attributes.shooting.three_point > 65:
            # Spot up on the arc
            return basket + direction * 24.0
        else:
            return basket + direction * 14.0

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

        # Account for separation from dribble moves
        effective_def_dist = def_dist + handler.fsm.defender_separation * 0.3

        openness = clamp((effective_def_dist - 2.0) / 6.0, 0.0, 1.0)
        rating_factor = base_rating / 99.0
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

        # Dribble move separation bonus
        sep_bonus = handler.fsm.defender_separation * 0.02

        return clamp(result.quality * 0.6 + drive_skill * 0.4 + sep_bonus, 0.0, 1.0)

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

    # -- Micro-action execution -----------------------------------------------

    def _execute_screen(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> bool:
        """Execute a screen action using the full screen mechanics.

        Returns True if the screen was set successfully (handler gets
        advantage), False if it resulted in a foul or was ineffective.
        """
        if self._pending_screener_id is None:
            return False

        screener_pcs = self.court.get_player_state(self._pending_screener_id)
        if screener_pcs is None:
            self._pending_screener_id = None
            return False

        player = handler.player
        screener = screener_pcs.player
        basket = self.court.basket_position(home_on_offense)

        # Find the on-ball defender
        closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
        if closest_def is None:
            self._pending_screener_id = None
            return False

        defender = closest_def.player

        # Evaluate screen quality
        screen_result = evaluate_screen(
            screen_type=ScreenType.BALL_SCREEN,
            screener_strength=screener.attributes.athleticism.strength,
            screener_weight=screener.body.weight_lbs,
            screener_screen_rating=screener.attributes.playmaking.screen_setting
            if hasattr(screener.attributes.playmaking, "screen_setting")
            else 65,
            defender_strength=defender.attributes.athleticism.strength,
            defender_weight=defender.body.weight_lbs,
            is_stationary=self._rng.random() < 0.85,
            moving_screen_detection=0.4,
            rng=self._phys_rng,
        )

        # Moving screen called - foul on screener
        if screen_result.moving_screen_called:
            self._pending_screener_id = None
            # Record offensive foul as turnover
            self._turnover(handler, home_on_offense)
            return False

        # Evaluate PnR defensive coverage
        coverage_type = self._rng.choice([
            PnRCoverageType.DROP, PnRCoverageType.SWITCH,
            PnRCoverageType.HEDGE, PnRCoverageType.BLITZ,
        ])
        pnr_result = evaluate_pnr_coverage(
            coverage=coverage_type,
            handler_ball_handle=player.attributes.playmaking.ball_handle,
            handler_three_point=player.attributes.shooting.three_point,
            screener_roll_rating=max(
                screener.attributes.finishing.layup,
                screener.attributes.finishing.standing_dunk,
            ),
            screener_can_shoot=screener.attributes.shooting.mid_range > 70,
            defender_lateral=defender.attributes.defense.lateral_quickness,
            big_defender_perimeter=50,
        )

        # Update FSMs
        handler.fsm.transition_to(
            BallHandlerState.USING_SCREEN,
            ticks=self._rng.randint(5, 10),
            target=handler.position + (basket - handler.position).normalized() * 5.0,
            intent=MovementIntent.SPRINT,
        )

        # Screener rolls or pops
        roller_or_popper = "roll"
        if screener.attributes.shooting.mid_range > 70 and self._rng.random() < 0.4:
            roller_or_popper = "pop"
            pop_target = screener_pcs.position + (
                screener_pcs.position - basket
            ).normalized() * 10.0
            screener_pcs.fsm.transition_to(
                OffBallOffenseState.POPPING,
                ticks=self._rng.randint(8, 15),
                target=pop_target,
                intent=MovementIntent.JOG,
            )
        else:
            screener_pcs.fsm.transition_to(
                OffBallOffenseState.ROLLING,
                ticks=self._rng.randint(8, 15),
                target=basket,
                intent=MovementIntent.SPRINT,
            )

        # Apply separation from screen
        handler.fsm.defender_separation += screen_result.separation_created

        # Emit screen event
        self._broadcast_event(ScreenEvent(
            screener_name=screener.full_name,
            handler_name=player.full_name,
            screen_type=ScreenType.BALL_SCREEN.value,
            defender_reaction=coverage_type.value,
            pnr_coverage=coverage_type.value,
            roller_or_popper=roller_or_popper,
            switch_occurred=pnr_result.mismatch_created,
            **self._make_base_fields(),
        ))

        # Consume screen time
        self._advance_clock(self._rng.uniform(1.0, 2.0))

        # Clear pending screener
        self._pending_screener_id = None
        return True

    def _execute_dribble_move(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> None:
        """Execute a dribble move using the full dribble system."""
        player = handler.player
        def_dist = self.court.defender_distance(player.id, home_on_offense)
        closest_def = self.court.closest_defender_to(handler.position, home_on_offense)

        # Select move type based on situation
        move_type = self._select_dribble_move(handler, def_dist)

        # Get defender attributes
        defender_lateral = 50
        defender_steal = 50
        if closest_def:
            defender_lateral = closest_def.player.attributes.defense.lateral_quickness
            defender_steal = closest_def.player.attributes.defense.steal

        # Resolve the dribble move
        result = resolve_dribble_move(
            ball_handle=player.attributes.playmaking.ball_handle,
            energy_pct=handler.energy.pct,
            defender_lateral=defender_lateral,
            defender_steal=defender_steal,
            move_type=move_type,
            has_ankle_breaker_badge=player.badges.has_badge("ankle_breaker"),
            badge_tier=player.badges.tier_value("ankle_breaker"),
            rng=self._phys_rng,
        )

        # Update FSM state
        spec = DRIBBLE_MOVES[move_type]
        ticks = max(3, int(spec.time_cost / TICK_DURATION))

        handler.fsm.transition_to(
            BallHandlerState.EXECUTING_DRIBBLE_MOVE,
            ticks=ticks,
            target=handler.position,
            intent=MovementIntent.STAND,
            context={"move_type": move_type.value, "result": result},
        )

        # Apply results
        handler.energy.drain(result.energy_cost)

        # Emit rich dribble move event
        def_name = closest_def.player.full_name if closest_def else ""
        self._broadcast_event(DribbleMoveEvent(
            player_name=player.full_name,
            player_id=player.id,
            move_type=move_type.value,
            success=result.success,
            separation_gained=result.separation,
            ankle_breaker=result.ankle_breaker,
            defender_name=def_name,
            combo_count=handler.fsm.combo_count,
            turnover=result.turnover,
            **self._make_base_fields(),
        ))

        if result.success:
            handler.fsm.defender_separation += result.separation
            handler.fsm.increment_combo(True)

            if result.ankle_breaker:
                self._possession_events.append(PossessionEvent(
                    event_type=PossessionEventType.ANKLE_BREAKER,
                    player_id=player.id,
                    description=f"{player.full_name} with the ankle breaker!",
                ))
                if self.narration:
                    ev = NarrationEvent(
                        text=f"{player.full_name} with the {move_type.value}... "
                             f"ANKLE BREAKER! Defender is stumbling!",
                    )
                    self._emit("ankle_breaker", ev, {"player_id": player.id})
        else:
            handler.fsm.reset_combo()
            if result.turnover:
                self._turnover(handler, home_on_offense)
                return

        # Consume time
        self._advance_clock(spec.time_cost)

    def _select_dribble_move(
        self, handler: PlayerCourtState, def_dist: float,
    ) -> DribbleMoveType:
        """Select the best dribble move for the situation."""
        player = handler.player

        # Available moves based on skill
        ball_handle = player.attributes.playmaking.ball_handle
        candidates: list[tuple[DribbleMoveType, float]] = []

        # Always available
        candidates.append((DribbleMoveType.CROSSOVER, 1.0))
        candidates.append((DribbleMoveType.HESITATION, 0.8))
        candidates.append((DribbleMoveType.IN_AND_OUT, 0.7))
        candidates.append((DribbleMoveType.BETWEEN_THE_LEGS, 0.6))

        # Skill-gated
        if ball_handle > 70:
            candidates.append((DribbleMoveType.BEHIND_THE_BACK, 0.7))
            candidates.append((DribbleMoveType.SPIN_MOVE, 0.6))
        if ball_handle > 80:
            candidates.append((DribbleMoveType.STEP_BACK, 0.8))
            candidates.append((DribbleMoveType.SNATCH_BACK, 0.7))
            candidates.append((DribbleMoveType.HARDEN_STEP_BACK, 0.6))
        if ball_handle > 90:
            candidates.append((DribbleMoveType.SHAMGOD, 0.3))

        # Situation modifiers
        if def_dist < 3.0:
            # Aggressive moves when defender is tight
            for i, (mt, w) in enumerate(candidates):
                if mt in (DribbleMoveType.CROSSOVER, DribbleMoveType.SPIN_MOVE):
                    candidates[i] = (mt, w * 1.5)
        elif def_dist > 5.0:
            # Setup moves when defender is sagging
            for i, (mt, w) in enumerate(candidates):
                if mt in (DribbleMoveType.HESITATION, DribbleMoveType.IN_AND_OUT):
                    candidates[i] = (mt, w * 1.3)

        # Combo bonus: chain moves
        if handler.fsm.combo_count > 0 and handler.fsm.combo_count < 3:
            for i, (mt, w) in enumerate(candidates):
                candidates[i] = (mt, w * 1.2)

        weights = [w for _, w in candidates]
        moves = [m for m, _ in candidates]
        return self._ai_rng.choices(moves, weights=weights, k=1)[0]

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

        # Factor in dribble move separation
        effective_def_dist = def_dist + handler.fsm.defender_separation * 0.3
        contest_quality = clamp(1.0 - effective_def_dist / 6.0, 0.0, 1.0)

        rim_protector = any(
            d.position.distance_to(basket) < 8.0
            and d.player.attributes.defense.block > 70
            for d in self.court.defensive_players(home_on_offense)
        )

        stats = self._player_stats(player.id, is_home)
        ctx = ShotContext(
            base_rating=base_rating,
            energy_pct=handler.energy.pct,
            is_open=effective_def_dist > 4.0,
            is_catch_and_shoot=catch_and_shoot,
            is_off_dribble=not catch_and_shoot,
            hot_cold_modifier=self.confidence.get(player.id),
            shot_distance=dist,
            contest_distance=effective_def_dist,
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

        # Update FSM to shooting state
        handler.fsm.transition_to(
            BallHandlerState.PULLING_UP,
            ticks=self._rng.randint(3, 5),
            target=handler.position,
            intent=MovementIntent.STAND,
        )

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

            # Emit rich shot result event + update broadcast stats
            assist_name = ""
            if self._last_passer_id and self._last_passer_id != player.id:
                passer_pcs = self.court.get_player_state(self._last_passer_id)
                if passer_pcs:
                    assist_name = passer_pcs.player.full_name
                    if self.broadcast_stats:
                        self.broadcast_stats.on_assist(
                            self._last_passer_id, assist_name,
                        )

            if self.broadcast_stats:
                self.broadcast_stats.on_made_shot(
                    player.id, player.full_name, is_home,
                    points, is_three, gs.clock.game_clock,
                )

            self._broadcast_event(ShotResultEvent(
                shooter_name=player.full_name,
                shooter_id=player.id,
                made=True,
                points=points,
                distance=dist,
                zone=zone_info.name,
                is_three=is_three,
                is_and_one=is_and_one,
                team_name=self._team_name(is_home),
                new_score_home=gs.score.home,
                new_score_away=gs.score.away,
                lead=gs.score.diff if is_home else -gs.score.diff,
                assist_player_name=assist_name,
                **self._make_base_fields(),
            ))

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

            # Reset dribble separation
            handler.fsm.defender_separation = 3.0
            handler.fsm.reset_combo()
        else:
            stats.record_missed_shot(is_three=is_three)
            self.confidence.on_missed_shot(player.id)
            if self.broadcast_stats:
                self.broadcast_stats.on_missed_shot(
                    player.id, player.full_name, is_home, is_three,
                )

            # Block check
            blocked = False
            closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
            if closest_def and def_dist < 3.0:
                block_chance = closest_def.player.attributes.defense.block / 99.0 * 0.15
                if self._phys_rng.random() < block_chance:
                    blocked = True
                    blk_stats = self._player_stats(closest_def.player_id, not is_home)
                    blk_stats.blocks += 1
                    if self.broadcast_stats:
                        self.broadcast_stats.on_block(
                            closest_def.player_id, closest_def.player.full_name,
                        )
                    self._broadcast_event(BlockEvent(
                        blocker_name=closest_def.player.full_name,
                        blocker_id=closest_def.player_id,
                        shooter_name=player.full_name,
                        shooter_id=player.id,
                        **self._make_base_fields(),
                    ))
                    if self.narration:
                        ev = self.narration.narrate_block(
                            blocker=closest_def.player.full_name,
                            shooter=player.full_name,
                        )
                        self._emit("block", ev, {})

            if not blocked:
                self._broadcast_event(ShotResultEvent(
                    shooter_name=player.full_name,
                    shooter_id=player.id,
                    made=False,
                    points=0,
                    distance=dist,
                    zone=zone_info.name,
                    is_three=is_three,
                    team_name=self._team_name(is_home),
                    new_score_home=gs.score.home,
                    new_score_away=gs.score.away,
                    **self._make_base_fields(),
                ))
                if self.narration:
                    ev = self.narration.narrate_missed_shot(
                        shooter=player.full_name, distance=dist, zone=zone_info.name,
                    )
                    self._emit("missed_shot", ev, {"player_id": player.id})

            # Rebound
            self._resolve_rebound(home_on_offense)

            handler.fsm.defender_separation = 3.0
            handler.fsm.reset_combo()

    def _execute_drive(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> bool:
        """Execute a drive with micro-action integration. Returns True if resolved."""
        gs = self.game_state
        player = handler.player
        is_home = home_on_offense
        basket = self.court.basket_position(home_on_offense)

        # Transition to driving state
        handler.fsm.transition_to(
            BallHandlerState.DRIVING,
            ticks=self._rng.randint(8, 15),
            target=basket,
            intent=MovementIntent.SPRINT,
        )

        # Emit drive initiation event
        closest_def = self.court.closest_defender_to(handler.position, home_on_offense)
        def_name = closest_def.player.full_name if closest_def else ""
        self._broadcast_event(DriveEvent(
            driver_name=player.full_name,
            driver_id=player.id,
            defender_name=def_name,
            distance_to_basket=handler.position.distance_to(basket),
            **self._make_base_fields(),
        ))

        # Move handler toward basket
        to_basket = (basket - handler.position).normalized()
        drive_dist = attribute_to_range(player.attributes.athleticism.speed, 5.0, 10.0)
        handler.position = Vec2(
            clamp(handler.position.x + to_basket.x * drive_dist, 0, COURT_LENGTH),
            clamp(handler.position.y + to_basket.y * drive_dist, 0, COURT_WIDTH),
        )
        if handler.kinematics:
            handler.kinematics.position = handler.position.copy()
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

        # Kick-out decision (30% chance if not close to basket)
        new_dist = handler.position.distance_to(basket)
        if new_dist > 10.0 and self._phys_rng.random() < 0.3:
            return False

        # At-rim: select finishing move
        rim_protector = any(
            d.player.attributes.defense.block > 70
            for d in self.court.defensive_players(home_on_offense)
            if d.position.distance_to(basket) < 8.0
        )

        finish = select_finish_type(
            layup=player.attributes.finishing.layup,
            driving_dunk=player.attributes.finishing.driving_dunk,
            standing_dunk=player.attributes.finishing.standing_dunk,
            acrobatic_finish=player.attributes.finishing.acrobatic_finish,
            post_hook=player.attributes.finishing.post_hook,
            vertical_leap=player.attributes.athleticism.vertical_leap,
            speed=player.attributes.athleticism.speed,
            defender_distance=def_dist,
            rim_protector_present=rim_protector,
            has_contact_finisher=player.badges.has_badge("contact_finisher"),
            has_slithery_finisher=player.badges.has_badge("slithery_finisher"),
            has_posterizer=player.badges.has_badge("posterizer"),
            has_acrobat=player.badges.has_badge("acrobat"),
            is_putback=False,
            rng=self._phys_rng,
        )

        # Transition to finishing state
        handler.fsm.transition_to(
            BallHandlerState.FINISHING,
            ticks=self._rng.randint(3, 6),
            target=basket,
            intent=MovementIntent.SPRINT,
            context={"finish_type": finish.finish_type.value},
        )

        # Resolve the finish
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
            rim_protector_present=rim_protector,
            is_clutch=gs.clock.is_clutch_time(),
            clutch_rating=player.attributes.mental.clutch,
        )
        make_prob = calculate_shot_probability(ctx)
        make_prob += finish.success_modifier
        make_prob = clamp(make_prob, 0.05, 0.95)
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
                    points=2, distance=new_dist, zone="paint",
                    lead=gs.score.diff if is_home else -gs.score.diff,
                    is_dunk=finish.is_dunk,
                )
                self._emit("made_shot", ev, {"player_id": player.id, "points": 2})
            if finish.is_dunk:
                self.momentum.on_dunk(is_home)

            # And-one check on drives
            if self._phys_rng.random() < finish.foul_draw_chance:
                self._free_throws(handler, 1, is_home)
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
        """Execute a pass with pass type selection. Returns True if stolen."""
        player = handler.player
        is_home = home_on_offense
        target = self.court.get_player_state(target_id)
        if target is None:
            return False

        # Select pass type based on situation
        dist = handler.position.distance_to(target.position)
        basket = self.court.basket_position(home_on_offense)
        target_dist_to_basket = target.position.distance_to(basket)

        pass_type = self._select_pass_type(handler, target, dist, target_dist_to_basket)

        # Update FSM to passing state
        handler.fsm.transition_to(
            BallHandlerState.PASSING,
            ticks=self._rng.randint(3, 6),
            target=target.position,
            intent=MovementIntent.STAND,
            context={"pass_type": pass_type.value, "target_id": target_id},
        )

        defenders = self.court.defensive_players(home_on_offense)
        def_positions = [d.position for d in defenders]
        lane = analyze_passing_lane(
            passer_pos=handler.position,
            receiver_pos=target.position,
            defender_positions=def_positions,
        )

        # Use the full pass resolution system
        def_dist = self.court.defender_distance(handler.player_id, home_on_offense)
        result = resolve_pass(
            pass_accuracy=player.attributes.playmaking.pass_accuracy,
            pass_vision=player.attributes.playmaking.pass_vision,
            receiver_hands=target.player.attributes.rebounding.box_out,  # Using as proxy
            pass_type=pass_type,
            distance=dist,
            lane_quality=lane.quality,
            is_under_pressure=def_dist < 3.0,
            has_needle_threader=player.badges.has_badge("needle_threader"),
            has_bail_out=player.badges.has_badge("bail_out"),
            rng=self._phys_rng,
        )

        if result.turnover:
            if result.intercepted:
                stealer = min(
                    defenders,
                    key=lambda d: d.position.distance_to(
                        (handler.position + target.position) * 0.5,
                    ),
                ) if defenders else None
                self._steal(handler, stealer, is_home)
            else:
                self._turnover(handler, is_home)
            return True

        # Successful pass -- emit broadcast event
        self._broadcast_event(PassEvent(
            passer_name=player.full_name,
            passer_id=player.id,
            receiver_name=target.player.full_name,
            receiver_id=target_id,
            pass_type=pass_type.value,
            distance=dist,
            is_entry_pass=target.position.distance_to(basket) < 10.0,
            is_skip_pass=dist > 25.0,
            is_kick_out=handler.fsm.current_state == BallHandlerState.DRIVING,
            lane_quality=lane.quality,
            **self._make_base_fields(),
        ))

        self._last_passer_id = handler.player_id
        self.court.ball.holder_id = target_id
        self.court.ball.status = BallStatus.HELD

        # Target enters receiving state then decides
        target.fsm.transition_to(
            OffBallOffenseState.RECEIVING_PASS,
            ticks=self._rng.randint(3, 5),
            target=target.position,
            intent=MovementIntent.STAND,
        )

        # After receiving, new handler gets DRIBBLING_IN_PLACE or TRIPLE_THREAT
        # This will be handled on the next tick when the FSM completes

        # Consume pass time
        pass_time = self._rng.uniform(0.5, 1.5)
        self._advance_clock(pass_time)
        if self._check_quarter_end():
            return True

        # Dimer badge: boost receiver's shooting
        if player.badges.has_badge("dimer"):
            target.fsm.context["dimer_boost"] = True

        return False

    def _select_pass_type(
        self,
        handler: PlayerCourtState,
        target: PlayerCourtState,
        distance: float,
        target_dist_to_basket: float,
    ) -> PassType:
        """Select the best pass type for the situation."""
        # Short distance perimeter pass
        if distance < 15.0 and target_dist_to_basket > 20.0:
            return PassType.CHEST

        # Entry pass to post
        if target_dist_to_basket < 10.0:
            return self._rng.choice([PassType.BOUNCE, PassType.LOB])

        # Skip pass (long distance)
        if distance > 25.0:
            return self._rng.choice([PassType.BULLET, PassType.OVERHEAD])

        # Kick-out from drive
        if handler.fsm.current_state == BallHandlerState.DRIVING:
            return PassType.BOUNCE

        # Default
        return self._rng.choice([PassType.CHEST, PassType.BOUNCE])

    def _execute_post_up(
        self, handler: PlayerCourtState, home_on_offense: bool,
    ) -> None:
        """Execute a post-up move."""
        gs = self.game_state
        player = handler.player
        is_home = home_on_offense
        basket = self.court.basket_position(home_on_offense)

        handler.fsm.transition_to(
            BallHandlerState.POSTING_UP,
            ticks=self._rng.randint(15, 30),
            target=basket,
            intent=MovementIntent.JOG,
        )

        to_basket = (basket - handler.position).normalized()
        handler.position = Vec2(
            clamp(handler.position.x + to_basket.x * 3.0, 0, COURT_LENGTH),
            clamp(handler.position.y + to_basket.y * 3.0, 0, COURT_WIDTH),
        )
        if handler.kinematics:
            handler.kinematics.position = handler.position.copy()
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
            self.court.ball.holder_id = pcs.player_id
            self.court.ball.status = BallStatus.HELD
            self.game_state.clock.shot_clock = min(14.0, self.game_state.clock.game_clock)
        else:
            stats.defensive_rebounds += 1
            # Evaluate transition opportunity after defensive rebound
            self._evaluate_transition_opportunity(pcs, home_on_offense, is_steal=False)

        if self.broadcast_stats:
            self.broadcast_stats.on_rebound(pcs.player_id, pcs.player.full_name, is_oreb)
        self._broadcast_event(ReboundEvent(
            rebounder_name=pcs.player.full_name,
            rebounder_id=pcs.player_id,
            is_offensive=is_oreb,
            **self._make_base_fields(),
        ))

    def _evaluate_transition_opportunity(
        self, ball_player: PlayerCourtState, home_on_offense: bool, is_steal: bool,
    ) -> None:
        """Evaluate whether to push in transition after a rebound or steal."""
        # The new offense is the opposite of whoever was on offense
        new_off_is_home = not home_on_offense
        new_offense = self.court.home_on_court if new_off_is_home else self.court.away_on_court
        new_defense = self.court.away_on_court if new_off_is_home else self.court.home_on_court
        basket = self.court.basket_position(new_off_is_home)

        offense_data = [
            (p.player_id, p.position, p.player.attributes.athleticism.speed)
            for p in new_offense
        ]
        defense_data = [
            (p.player_id, p.position, p.player.attributes.athleticism.speed)
            for p in new_defense
        ]

        trans_result = evaluate_transition(
            rebounder_speed=ball_player.player.attributes.athleticism.speed,
            rebounder_transition_tendency=getattr(
                ball_player.player.tendencies, "transition_tendency", 0.5,
            ),
            offense_positions=offense_data,
            defense_positions=defense_data,
            basket_position=basket,
            is_steal=is_steal,
            rng=self._rng,
        )

        if trans_result.should_push:
            self._is_transition = True

    def _turnover(self, handler: PlayerCourtState, is_home: bool) -> None:
        stats = self._player_stats(handler.player_id, is_home)
        stats.turnovers += 1
        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.turnovers += 1
        self.confidence.on_turnover(handler.player_id)
        self.momentum.on_turnover(is_home)
        if self.broadcast_stats:
            self.broadcast_stats.on_turnover(handler.player_id, handler.player.full_name)
        self._broadcast_event(TurnoverEvent(
            player_name=handler.player.full_name,
            player_id=handler.player_id,
            is_steal=False,
            team_name=self._team_name(is_home),
            **self._make_base_fields(),
        ))
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
            if self.broadcast_stats:
                self.broadcast_stats.on_steal(stealer.player_id, stealer_name)
            # Evaluate transition opportunity after steal
            self._evaluate_transition_opportunity(stealer, is_home, is_steal=True)

        if self.broadcast_stats:
            self.broadcast_stats.on_turnover(handler.player_id, handler.player.full_name)
        self._broadcast_event(TurnoverEvent(
            player_name=handler.player.full_name,
            player_id=handler.player_id,
            is_steal=True,
            stealer_name=stealer_name,
            stealer_id=stealer.player_id if stealer else 0,
            team_name=self._team_name(is_home),
            **self._make_base_fields(),
        ))

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
            if self.broadcast_stats:
                self.broadcast_stats.on_foul(closest.player_id, closest.player.full_name)
            self._broadcast_event(FoulEvent(
                fouler_name=closest.player.full_name,
                fouler_id=closest.player_id,
                victim_name=handler.player.full_name,
                victim_id=handler.player_id,
                team_fouls=gs.away_team_fouls if is_home else gs.home_team_fouls,
                personal_fouls=closest.fouls,
                free_throws_awarded=2,
                is_foul_trouble=closest.fouls >= 4,
                **self._make_base_fields(),
            ))
            if self.narration:
                ev = self.narration.narrate_foul(
                    fouler=closest.player.full_name,
                    player=handler.player.full_name,
                    team_fouls=gs.away_team_fouls if is_home else gs.home_team_fouls,
                    fts=2,
                )
                self._emit("foul", ev, {})
        self._free_throws(handler, 2, is_home)

    def _shot_clock_violation(self, home_on_offense: bool) -> None:
        """Handle a shot clock violation."""
        is_home = home_on_offense
        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.turnovers += 1
        self._broadcast_event(TurnoverEvent(
            player_name="",
            player_id=0,
            is_steal=False,
            team_name=self._team_name(is_home),
            **self._make_base_fields(),
        ))
        if self.narration:
            ev = NarrationEvent(
                text=f"Shot clock violation! Turnover, {self._team_name(not is_home)} ball.",
            )
            self._emit("shot_clock_violation", ev, {})

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
                if self.broadcast_stats:
                    self.broadcast_stats.on_made_shot(
                        player.id, player.full_name, is_home, 1, False,
                        gs.clock.game_clock,
                    )
            else:
                stats.record_missed_ft()
            self._broadcast_event(FreeThrowEvent(
                shooter_name=player.full_name,
                shooter_id=player.id,
                made=made,
                attempt_number=_ + 1,
                total_attempts=count,
                **self._make_base_fields(),
            ))
            if self.narration:
                ev = self.narration.narrate_free_throw(shooter=player.full_name, made=made)
                self._emit("free_throw", ev, {"made": made})

    # -- Energy ---------------------------------------------------------------

    def _drain_energy_for_ticks(self, num_ticks: int) -> None:
        """Drain energy for on-court players for a given number of ticks."""
        for pcs in self.court.all_on_court():
            pcs.energy.drain(ENERGY_DRAIN_JOG * num_ticks)
        for pcs in self.court.home_bench + self.court.away_bench:
            pcs.energy.recover(ENERGY_RECOVERY_BENCH * num_ticks)
        # Track minutes
        seconds = num_ticks * TICK_DURATION
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
            # Initialize kinematics for incoming player
            in_pcs.init_kinematics()
            # Emit substitution event
            self._broadcast_event(SubstitutionEvent(
                player_in_name=in_pcs.player.full_name,
                player_in_id=in_pcs.player_id,
                player_out_name=out_pcs.player.full_name,
                player_out_id=out_pcs.player_id,
                team_name=self._team_name(is_home),
                **self._make_base_fields(),
            ))

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
        remaining = gs.home_timeouts if is_home else gs.away_timeouts
        self._broadcast_event(TimeoutEvent(
            team_name=self._team_name(is_home),
            timeouts_remaining=remaining,
            opponent_run=self._opponent_run,
            score_diff=gs.score.diff if is_home else -gs.score.diff,
            **self._make_base_fields(),
        ))
        if self.narration:
            ev = self.narration.narrate_timeout(
                team=self._team_name(is_home), remaining=remaining,
            )
            self._emit("timeout", ev, {})

    # -- Helpers --------------------------------------------------------------

    @staticmethod
    def _intent_to_movement_type(intent: MovementIntent) -> MovementType:
        """Convert FSM movement intent to physics movement type."""
        mapping = {
            MovementIntent.STAND: MovementType.STAND,
            MovementIntent.WALK: MovementType.WALK,
            MovementIntent.JOG: MovementType.JOG,
            MovementIntent.SPRINT: MovementType.SPRINT,
            MovementIntent.LATERAL: MovementType.LATERAL,
            MovementIntent.BACKPEDAL: MovementType.BACKPEDAL,
        }
        return mapping.get(intent, MovementType.JOG)

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

    def _broadcast_event(self, event) -> None:
        """Feed a rich narration event into the broadcast mixer."""
        if self.broadcast_mixer is not None:
            self.broadcast_mixer.add_event(event)

    def _make_base_fields(self) -> dict:
        """Return common fields for narration events."""
        gs = self.game_state
        return {
            "game_clock": gs.clock.game_clock,
            "shot_clock": gs.clock.shot_clock,
            "quarter": gs.clock.quarter,
            "home_score": gs.score.home,
            "away_score": gs.score.away,
            "possession_id": self._total_possessions,
        }
