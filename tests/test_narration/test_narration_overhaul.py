"""Tests for the broadcast-quality narration overhaul.

Covers all new modules: chain_composer, spatial, clock_narrator,
analyst, game_memory, pacing, segments, and updated action_chain,
possession_narrator, events, and calibration targets.
"""

from __future__ import annotations

import pytest

from hoops_sim.narration.action_chain import ActionChainTracker
from hoops_sim.narration.analyst import AnalystVoice
from hoops_sim.narration.chain_composer import ChainComposer
from hoops_sim.narration.clock_narrator import ClockNarrator, IntensityLevel
from hoops_sim.narration.events import (
    BallAdvanceEvent,
    CrowdReactionEvent,
    DribbleMoveEvent,
    DriveEvent,
    MismatchEvent,
    MomentumEvent,
    MomentumKind,
    NarrationEventType,
    PassEvent,
    PlayCallEvent,
    ProbingEvent,
    ScreenEvent,
    ShotClockPressureEvent,
    ShotResultEvent,
    TimeoutEvent,
    TurnoverEvent,
    FoulEvent,
)
from hoops_sim.narration.game_memory import GameMemory
from hoops_sim.narration.narrative_arc import ArcSnapshot, NarrativeArcTracker
from hoops_sim.narration.pacing import PacingManager, VerbosityBand
from hoops_sim.narration.possession_narrator import (
    PossessionNarrator,
    _compute_importance,
)
from hoops_sim.narration.segments import BroadcastSegments
from hoops_sim.narration.spatial import SpatialDescriber
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.narration.play_by_play import PlayByPlayNarrator
from hoops_sim.narration.color_commentary import ColorCommentaryNarrator
from hoops_sim.calibration.narration_targets import NarrationCalibrationResult
from hoops_sim.utils.rng import SeededRNG


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rng():
    return SeededRNG(42)


@pytest.fixture
def stat_tracker():
    return LiveStatTracker(home_team="Hawks", away_team="Celtics")


@pytest.fixture
def arc_tracker(stat_tracker):
    return NarrativeArcTracker(
        home_team="Hawks", away_team="Celtics", stat_tracker=stat_tracker,
    )


# ---------------------------------------------------------------------------
# Phase 1: Action chain tracker tests
# ---------------------------------------------------------------------------


class TestActionChainTracker:
    def test_add_and_retrieve(self):
        chain = ActionChainTracker()
        chain.add("dribble_move", "Mitchell", "crossover", detail="crossover")
        chain.add("drive", "Mitchell", "drives left", detail="left")
        assert len(chain.entries) == 2
        assert chain.had_dribble_move()
        assert chain.had_drive()
        assert not chain.had_pass()

    def test_dribble_combo_count(self):
        chain = ActionChainTracker()
        chain.add("dribble_move", "Mitchell", "hesi", detail="hesitation")
        chain.add("dribble_move", "Mitchell", "cross", detail="crossover")
        chain.add("dribble_move", "Mitchell", "btb", detail="behind_the_back")
        assert chain.dribble_combo_count == 3

    def test_dribble_combo_broken_by_drive(self):
        chain = ActionChainTracker()
        chain.add("dribble_move", "Mitchell", "cross", detail="crossover")
        chain.add("drive", "Mitchell", "drives left")
        assert chain.dribble_combo_count == 0  # drive broke the streak

    def test_build_shot_context_with_screen(self):
        chain = ActionChainTracker()
        chain.add("screen", "Davis", "sets the screen")
        chain.add("dribble_move", "Mitchell", "crossover", detail="crossover")
        context = chain.build_shot_context("Mitchell")
        assert "Davis" in context

    def test_build_shot_context_empty(self):
        chain = ActionChainTracker()
        assert chain.build_shot_context("Anyone") == ""

    def test_chain_descriptions(self):
        chain = ActionChainTracker()
        chain.add("dribble_move", "A", "crosses over")
        chain.add("drive", "A", "drives left")
        assert chain.chain_descriptions == ["crosses over", "drives left"]

    def test_max_entries(self):
        chain = ActionChainTracker(max_entries=3)
        for i in range(5):
            chain.add("dribble_move", "A", f"move {i}")
        assert len(chain.entries) == 3

    def test_clear(self):
        chain = ActionChainTracker()
        chain.add("dribble_move", "A", "cross")
        chain.tick()
        chain.tick()
        chain.clear()
        assert len(chain.entries) == 0
        assert chain._tick_counter == 0


# ---------------------------------------------------------------------------
# Phase 1: Importance scoring tests
# ---------------------------------------------------------------------------


class TestImportanceScoring:
    def test_terminal_events_always_max(self):
        shot = ShotResultEvent(shooter_name="A", made=True, points=2)
        assert _compute_importance(shot) == 1.0

    def test_dribble_base_importance(self):
        dribble = DribbleMoveEvent(
            player_name="A", move_type="crossover", success=True,
        )
        score = _compute_importance(dribble)
        assert 0.5 < score < 0.8

    def test_ankle_breaker_higher_importance(self):
        dribble = DribbleMoveEvent(
            player_name="A", move_type="crossover",
            success=True, ankle_breaker=True,
        )
        score = _compute_importance(dribble)
        assert score >= 0.8

    def test_ball_advance_low_importance(self):
        advance = BallAdvanceEvent(ball_handler_name="A")
        score = _compute_importance(advance)
        assert score == 0.3

    def test_drive_high_importance(self):
        drive = DriveEvent(driver_name="A")
        score = _compute_importance(drive)
        assert score >= 0.7

    def test_kickout_pass_higher(self):
        p = PassEvent(passer_name="A", receiver_name="B", is_kick_out=True)
        score = _compute_importance(p)
        assert score >= 0.7

    def test_screen_with_switch_higher(self):
        s = ScreenEvent(
            screener_name="A", handler_name="B", switch_occurred=True,
        )
        score = _compute_importance(s)
        assert score >= 0.7


# ---------------------------------------------------------------------------
# Phase 2: Chain composer tests
# ---------------------------------------------------------------------------


class TestChainComposer:
    def test_compose_empty(self, rng):
        composer = ChainComposer(rng)
        assert composer.compose([]) == ""

    def test_single_dribble(self, rng):
        composer = ChainComposer(rng)
        events = [
            DribbleMoveEvent(
                player_name="Mitchell", move_type="crossover", success=True,
            ),
        ]
        result = composer.compose(events)
        assert "Mitchell" in result
        assert len(result) > 5

    def test_dribble_combo(self, rng):
        composer = ChainComposer(rng)
        events = [
            DribbleMoveEvent(
                player_name="Mitchell", move_type="hesitation", success=True,
            ),
            DribbleMoveEvent(
                player_name="Mitchell", move_type="crossover", success=True,
            ),
        ]
        result = composer.compose(events)
        assert "Mitchell" in result
        # Should join with ellipses (combo)
        assert "..." in result

    def test_screen_then_drive(self, rng):
        composer = ChainComposer(rng)
        events = [
            ScreenEvent(
                screener_name="Davis", handler_name="Mitchell",
                pnr_coverage="drop",
            ),
            DriveEvent(
                driver_name="Mitchell", defender_name="Williams",
            ),
        ]
        result = composer.compose(events)
        assert "Davis" in result or "Mitchell" in result

    def test_pass_chain(self, rng):
        composer = ChainComposer(rng)
        events = [
            PassEvent(
                passer_name="Mitchell", receiver_name="Davis",
                pass_type="chest",
            ),
            PassEvent(
                passer_name="Davis", receiver_name="Thompson",
                pass_type="chest",
            ),
        ]
        result = composer.compose(events)
        assert "Mitchell" in result or "Davis" in result

    def test_verbosity_affects_advance(self, rng):
        composer = ChainComposer(rng)
        events = [
            BallAdvanceEvent(ball_handler_name="Mitchell"),
        ]
        # Low verbosity should suppress advance
        result_low = composer.compose(events, verbosity=0.1)
        result_high = composer.compose(events, verbosity=0.5)
        # High verbosity should include advance
        assert len(result_high) >= len(result_low)

    def test_drive_with_kickout(self, rng):
        composer = ChainComposer(rng)
        events = [
            DriveEvent(
                driver_name="Mitchell", defender_name="Williams",
                kick_out=True, kick_out_target="Thompson",
            ),
        ]
        result = composer.compose(events)
        assert "Thompson" in result


# ---------------------------------------------------------------------------
# Phase 3: New event types tests
# ---------------------------------------------------------------------------


class TestNewEventTypes:
    def test_probing_event(self):
        event = ProbingEvent(
            player_name="Mitchell", defender_name="Williams",
            ticks_held=25,
        )
        assert event.event_type == NarrationEventType.PROBING

    def test_shot_clock_pressure_event(self):
        event = ShotClockPressureEvent(
            team_name="Hawks", handler_name="Mitchell",
            shot_clock=4.5,
        )
        assert event.event_type == NarrationEventType.SHOT_CLOCK_PRESSURE

    def test_play_call_event(self):
        event = PlayCallEvent(
            caller_name="Mitchell", play_name="pick and roll",
        )
        assert event.event_type == NarrationEventType.PLAY_CALL

    def test_mismatch_event(self):
        event = MismatchEvent(
            offensive_player_name="Davis",
            defensive_player_name="Williams",
            mismatch_type="size",
        )
        assert event.event_type == NarrationEventType.MISMATCH

    def test_crowd_reaction_event(self):
        event = CrowdReactionEvent(
            reaction_type="erupts", is_home_positive=True,
        )
        assert event.event_type == NarrationEventType.CROWD_REACTION

    def test_spatial_fields_on_base_event(self):
        event = ShotResultEvent(
            shooter_name="Mitchell", made=True, points=3,
            court_location="left wing",
            distance_description="from 24 feet",
        )
        assert event.court_location == "left wing"
        assert event.distance_description == "from 24 feet"


# ---------------------------------------------------------------------------
# Phase 4: Spatial describer tests
# ---------------------------------------------------------------------------


class TestSpatialDescriber:
    def test_describe_location_known_zone(self):
        result = SpatialDescriber.describe_location("three_left_wing")
        assert "left wing" in result

    def test_describe_location_top_key(self):
        result = SpatialDescriber.describe_location("three_top_key")
        assert "top of the key" in result

    def test_describe_location_unknown(self):
        result = SpatialDescriber.describe_location("unknown_zone_name")
        assert len(result) > 0

    def test_short_location(self):
        result = SpatialDescriber.short_location("restricted")
        assert result == "the rim"

    def test_describe_distance_close(self):
        assert "rim" in SpatialDescriber.describe_distance(3.0)

    def test_describe_distance_deep(self):
        assert "deep" in SpatialDescriber.describe_distance(27.0)

    def test_describe_distance_downtown(self):
        result = SpatialDescriber.describe_distance(35.0)
        assert "downtown" in result.lower()

    def test_shot_location_phrase_three(self):
        result = SpatialDescriber.shot_location_phrase(
            "three_left_wing", 27.0, is_three=True,
        )
        assert "deep" in result or "wing" in result

    def test_shot_location_phrase_rim(self):
        result = SpatialDescriber.shot_location_phrase(
            "restricted", 3.0, is_three=False,
        )
        assert "rim" in result

    def test_relative_position_same_spot(self):
        result = SpatialDescriber.relative_position_phrase(
            "left wing", "left wing",
        )
        assert result is not None
        assert "same spot" in result

    def test_relative_position_different(self):
        result = SpatialDescriber.relative_position_phrase(
            "left wing", "right corner",
        )
        assert result is None


# ---------------------------------------------------------------------------
# Phase 5: Clock narrator tests
# ---------------------------------------------------------------------------


class TestClockNarrator:
    def test_shot_clock_high_no_phrase(self, rng):
        cn = ClockNarrator(rng)
        assert cn.shot_clock_phrase(15.0) is None

    def test_shot_clock_low_has_phrase(self, rng):
        cn = ClockNarrator(rng)
        phrase = cn.shot_clock_phrase(3.0)
        assert phrase is not None
        assert len(phrase) > 5

    def test_shot_clock_medium(self, rng):
        cn = ClockNarrator(rng)
        phrase = cn.shot_clock_phrase(6.0)
        assert phrase is not None

    def test_game_clock_clutch_q4(self, rng):
        cn = ClockNarrator(rng)
        phrase = cn.game_clock_phrase(quarter=4, game_clock=25.0, score_diff=2)
        assert phrase is not None

    def test_game_clock_early_no_phrase(self, rng):
        cn = ClockNarrator(rng)
        phrase = cn.game_clock_phrase(quarter=1, game_clock=600.0, score_diff=5)
        assert phrase is None

    def test_clutch_shot_modifier_tie(self, rng):
        cn = ClockNarrator(rng)
        mod = cn.clutch_shot_modifier(
            quarter=4, game_clock=30.0, score_diff=-2, points=2,
        )
        assert mod is not None
        assert "TIE" in mod

    def test_clutch_shot_modifier_take_lead(self, rng):
        cn = ClockNarrator(rng)
        mod = cn.clutch_shot_modifier(
            quarter=4, game_clock=30.0, score_diff=-2, points=3,
        )
        assert mod is not None
        assert "LEAD" in mod

    def test_intensity_maximum(self, rng):
        cn = ClockNarrator(rng)
        level = cn.intensity_level(quarter=4, game_clock=60.0, score_diff=3)
        assert level == IntensityLevel.MAXIMUM

    def test_intensity_low_blowout(self, rng):
        cn = ClockNarrator(rng)
        level = cn.intensity_level(quarter=3, game_clock=400.0, score_diff=30)
        assert level == IntensityLevel.LOW

    def test_intensity_high_close_q4(self, rng):
        cn = ClockNarrator(rng)
        level = cn.intensity_level(quarter=4, game_clock=200.0, score_diff=5)
        assert level == IntensityLevel.HIGH


# ---------------------------------------------------------------------------
# Phase 6: Analyst voice tests
# ---------------------------------------------------------------------------


class TestAnalystVoice:
    def test_should_interject_on_timeout(self, rng, stat_tracker):
        analyst = AnalystVoice(rng, stat_tracker)
        event = TimeoutEvent(team_name="Hawks", timeouts_remaining=4)
        assert analyst.should_interject(event)

    def test_should_interject_on_momentum(self, rng, stat_tracker):
        analyst = AnalystVoice(rng, stat_tracker)
        event = MomentumEvent(
            kind=MomentumKind.RUN_EXTENDED,
            team_name="Hawks", run_points=10,
        )
        assert analyst.should_interject(event)

    def test_should_interject_on_foul_trouble(self, rng, stat_tracker):
        analyst = AnalystVoice(rng, stat_tracker)
        event = FoulEvent(
            fouler_name="Davis", is_foul_trouble=True,
            personal_fouls=4,
        )
        assert analyst.should_interject(event)

    def test_generate_shot_context(self, rng, stat_tracker):
        analyst = AnalystVoice(rng, stat_tracker)
        # Setup: player has enough shots for context
        for _ in range(6):
            stat_tracker.on_made_shot(1, "Mitchell", True, 2, False, 600.0)

        event = ShotResultEvent(
            shooter_name="Mitchell", shooter_id=1,
            made=True, points=2, team_name="Hawks",
        )
        arc = ArcSnapshot()
        text = analyst.generate(event, arc)
        assert text is not None

    def test_generate_timeout_context(self, rng, stat_tracker):
        analyst = AnalystVoice(rng, stat_tracker)
        event = TimeoutEvent(team_name="Hawks", timeouts_remaining=4)
        arc = ArcSnapshot()
        text = analyst.generate(event, arc)
        assert text is not None


# ---------------------------------------------------------------------------
# Phase 7: Game memory tests
# ---------------------------------------------------------------------------


class TestGameMemory:
    def test_record_and_callback_block_revenge(self, rng):
        mem = GameMemory(rng)
        mem.record_block(
            quarter=1, game_clock=600.0,
            blocker_id=2, blocker_name="Johnson",
            shooter_id=1, shooter_name="Mitchell",
        )
        callback = mem.check_callback(
            event_type="drive",
            player_id=1, player_name="Mitchell",
            opponent_id=2, opponent_name="Johnson",
        )
        assert callback is not None
        assert "revenge" in callback.lower() or "block" in callback.lower()

    def test_no_callback_unrelated(self, rng):
        mem = GameMemory(rng)
        mem.record_block(
            quarter=1, game_clock=600.0,
            blocker_id=2, blocker_name="Johnson",
            shooter_id=1, shooter_name="Mitchell",
        )
        callback = mem.check_callback(
            event_type="drive",
            player_id=3, player_name="Davis",
            opponent_id=4, opponent_name="Williams",
        )
        assert callback is None

    def test_zone_callback_same_spot(self, rng):
        mem = GameMemory(rng)
        # Record a miss from left wing
        mem.record_shot(
            quarter=1, game_clock=600.0,
            shooter_id=1, shooter_name="Mitchell",
            zone="left wing", made=False,
        )
        # Record another miss from same spot
        mem.record_shot(
            quarter=2, game_clock=400.0,
            shooter_id=1, shooter_name="Mitchell",
            zone="left wing", made=False,
        )
        # Now makes from same spot
        callback = mem.check_zone_callback(
            shooter_id=1, zone="left wing", made=True,
        )
        assert callback is not None

    def test_storyline_tracking(self, rng):
        mem = GameMemory(rng)
        mem.add_storyline("Mitchell vs Williams", "Great matchup", 0.7)
        storylines = mem.get_active_storylines()
        assert len(storylines) == 1
        assert storylines[0].name == "Mitchell vs Williams"

    def test_total_memorable_plays(self, rng):
        mem = GameMemory(rng)
        mem.record_block(1, 600.0, 2, "B", 1, "A")
        mem.record_ankle_breaker(1, 550.0, 1, "A", 2, "B")
        assert mem.total_memorable_plays == 2


# ---------------------------------------------------------------------------
# Phase 8: Pacing manager tests
# ---------------------------------------------------------------------------


class TestPacingManager:
    def test_score_verbosity_returns_float(self, rng):
        clock = ClockNarrator(rng)
        pm = PacingManager(clock_narrator=clock)
        events = [
            ShotResultEvent(
                shooter_name="A", made=True, points=2,
                quarter=1, game_clock=600.0,
                home_score=20, away_score=18,
            ),
        ]
        score = pm.score_verbosity(events, ArcSnapshot())
        assert 0.0 <= score <= 1.0

    def test_high_verbosity_clutch(self, rng):
        clock = ClockNarrator(rng)
        pm = PacingManager(clock_narrator=clock)
        events = [
            DribbleMoveEvent(
                player_name="A", move_type="crossover",
                quarter=4, game_clock=30.0,
                home_score=95, away_score=93,
            ),
            DriveEvent(
                driver_name="A",
                quarter=4, game_clock=28.0,
                home_score=95, away_score=93,
            ),
            ShotResultEvent(
                shooter_name="A", made=True, points=2,
                quarter=4, game_clock=25.0,
                home_score=95, away_score=93,
            ),
        ]
        score = pm.score_verbosity(events, ArcSnapshot())
        assert score >= 0.5  # Should be high for clutch play

    def test_low_verbosity_blowout(self, rng):
        clock = ClockNarrator(rng)
        pm = PacingManager(clock_narrator=clock)
        events = [
            ShotResultEvent(
                shooter_name="A", made=True, points=2,
                quarter=2, game_clock=400.0,
                home_score=60, away_score=30,
            ),
        ]
        score = pm.score_verbosity(events, ArcSnapshot())
        assert score < 0.5  # Should be low for blowout

    def test_verbosity_band_labels(self):
        assert VerbosityBand.label(0.1) == "LOW"
        assert VerbosityBand.label(0.4) == "MEDIUM"
        assert VerbosityBand.label(0.7) == "HIGH"
        assert VerbosityBand.label(0.9) == "MAXIMUM"

    def test_rhythm_smoothing(self, rng):
        clock = ClockNarrator(rng)
        pm = PacingManager(clock_narrator=clock)
        # Force several high-verbosity possessions
        for _ in range(4):
            events = [
                DribbleMoveEvent(
                    player_name="A", move_type="crossover",
                    quarter=4, game_clock=60.0,
                    home_score=95, away_score=93,
                ),
                DriveEvent(
                    driver_name="A",
                    quarter=4, game_clock=58.0,
                    home_score=95, away_score=93,
                ),
                ShotResultEvent(
                    shooter_name="A", made=True, points=2,
                    quarter=4, game_clock=55.0,
                    home_score=95, away_score=93,
                ),
            ]
            pm.score_verbosity(events, ArcSnapshot())
        # Average should exist
        assert pm.average_recent_verbosity > 0


# ---------------------------------------------------------------------------
# Phase 11: Broadcast segments tests
# ---------------------------------------------------------------------------


class TestBroadcastSegments:
    def test_quarter_intro_q2(self, rng, stat_tracker):
        stat_tracker.home_score = 28
        stat_tracker.away_score = 25
        segs = BroadcastSegments(rng, stat_tracker, "Hawks", "Celtics")
        text = segs.quarter_intro(2, ArcSnapshot())
        assert "Hawks" in text or "Celtics" in text
        assert "28" in text or "25" in text

    def test_quarter_intro_q4_close(self, rng, stat_tracker):
        stat_tracker.home_score = 82
        stat_tracker.away_score = 80
        segs = BroadcastSegments(rng, stat_tracker, "Hawks", "Celtics")
        text = segs.quarter_intro(4, ArcSnapshot())
        assert "wire" in text.lower() or "close" in text.lower() or "Final" in text

    def test_halftime_report(self, rng, stat_tracker):
        stat_tracker.home_score = 55
        stat_tracker.away_score = 48
        pstats = stat_tracker.get_player(1, "Mitchell")
        pstats.points = 18
        pstats.fg_made = 7
        pstats.fg_attempted = 12

        segs = BroadcastSegments(rng, stat_tracker, "Hawks", "Celtics")
        text = segs.halftime_report(ArcSnapshot())
        assert "HALFTIME" in text
        assert "Mitchell" in text

    def test_end_of_game_wrap(self, rng, stat_tracker):
        stat_tracker.home_score = 108
        stat_tracker.away_score = 102
        pstats = stat_tracker.get_player(1, "Mitchell")
        pstats.points = 32
        pstats.fg_made = 12
        pstats.fg_attempted = 22
        pstats.assists = 8
        pstats.rebounds = 5

        segs = BroadcastSegments(rng, stat_tracker, "Hawks", "Celtics")
        text = segs.end_of_game_wrap(ArcSnapshot())
        assert "FINAL" in text
        assert "108" in text
        assert "Mitchell" in text


# ---------------------------------------------------------------------------
# Integration: PossessionNarrator with ChainComposer
# ---------------------------------------------------------------------------


class TestPossessionNarratorWithComposer:
    def test_compose_with_chain_composer(self, rng, stat_tracker, arc_tracker):
        pbp = PlayByPlayNarrator(rng, stat_tracker)
        color = ColorCommentaryNarrator(rng, stat_tracker, arc_tracker)
        composer = ChainComposer(rng)
        narrator = PossessionNarrator(pbp, color, chain_composer=composer)

        narrator.start_possession()
        narrator.add_event(DribbleMoveEvent(
            player_name="Mitchell", move_type="hesitation", success=True,
        ))
        narrator.add_event(DribbleMoveEvent(
            player_name="Mitchell", move_type="crossover", success=True,
        ))
        narrator.add_event(DriveEvent(
            driver_name="Mitchell", defender_name="Williams",
        ))
        narrator.add_event(ShotResultEvent(
            shooter_name="Mitchell", made=True, points=2,
            team_name="Hawks", new_score_home=50, new_score_away=48,
            lead=2,
        ))

        narration = narrator.compose(ArcSnapshot())
        assert narration.has_content
        full = narration.full_text()
        assert "Mitchell" in full
        assert len(full) > 20

    def test_compose_without_chain_composer_backwards_compatible(
        self, rng, stat_tracker, arc_tracker,
    ):
        """Original behavior without chain composer should still work."""
        pbp = PlayByPlayNarrator(rng, stat_tracker)
        color = ColorCommentaryNarrator(rng, stat_tracker, arc_tracker)
        narrator = PossessionNarrator(pbp, color)

        narrator.start_possession()
        narrator.add_event(ShotResultEvent(
            shooter_name="Curry", made=True, points=3,
            distance=25.0, zone="Three Top Key", is_three=True,
            team_name="Warriors", new_score_home=60, new_score_away=55,
            lead=5,
        ))

        narration = narrator.compose(ArcSnapshot())
        assert narration.has_content
        assert "Curry" in narration.full_text()


# ---------------------------------------------------------------------------
# Calibration targets update tests
# ---------------------------------------------------------------------------


class TestUpdatedCalibration:
    def test_new_fields_default_zero(self):
        result = NarrationCalibrationResult(
            total_possessions=100, total_words=5000,
        )
        assert result.spatial_references == 0
        assert result.clock_references == 0
        assert result.callback_references == 0
        assert result.dribble_combo_chains == 0

    def test_summary_includes_new_fields(self):
        result = NarrationCalibrationResult(
            total_possessions=100, total_words=5000,
            spatial_references=65,
            clock_references=15,
            callback_references=8,
            dribble_combo_chains=20,
        )
        summary = result.summary()
        assert "Spatial references: 65" in summary
        assert "Clock references: 15" in summary
        assert "Callback references: 8" in summary

    def test_check_targets_updated_thresholds(self):
        result = NarrationCalibrationResult(
            total_possessions=100,
            total_words=5000,
        )
        issues = result.check_targets()
        # Should not flag words per possession (50 is within 25-120)
        wpp_issues = [i for i in issues if "Words per possession" in i]
        assert len(wpp_issues) == 0

    def test_spatial_reference_rate(self):
        result = NarrationCalibrationResult(
            total_possessions=100,
            total_words=5000,
            spatial_references=70,
        )
        assert result.spatial_reference_rate == 0.7
