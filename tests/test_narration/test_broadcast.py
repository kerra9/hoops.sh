"""Tests for the broadcast-quality narration system.

Covers: events, play-by-play narrator, color commentary, possession narrator,
broadcast mixer, stat tracker, narrative arc tracker, formatter, and
calibration targets.
"""

from __future__ import annotations

import pytest

from hoops_sim.narration.broadcast_mixer import BroadcastLine, BroadcastMixer, VerbosityLevel
from hoops_sim.calibration.narration_targets import NarrationCalibrationResult
from hoops_sim.narration.color_commentary import ColorCommentaryNarrator
from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    FoulEvent,
    FreeThrowEvent,
    MilestoneEvent,
    MomentumEvent,
    MomentumKind,
    NarrationEventType,
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
from hoops_sim.narration.formatter import BroadcastFormatter
from hoops_sim.narration.narrative_arc import ArcType, NarrativeArcTracker
from hoops_sim.narration.play_by_play import PlayByPlayNarrator
from hoops_sim.narration.possession_narrator import PossessionNarrator
from hoops_sim.narration.stat_tracker import LiveStatTracker, PlayerNarrationStats
from hoops_sim.utils.rng import SeededRNG


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rng():
    return SeededRNG(42)


@pytest.fixture
def stat_tracker():
    return LiveStatTracker(home_team="Celtics", away_team="Lakers")


@pytest.fixture
def arc_tracker(stat_tracker):
    return NarrativeArcTracker(
        home_team="Celtics", away_team="Lakers", stat_tracker=stat_tracker,
    )


@pytest.fixture
def pbp_narrator(rng, stat_tracker):
    return PlayByPlayNarrator(rng, stat_tracker)


@pytest.fixture
def color_narrator(rng, stat_tracker, arc_tracker):
    return ColorCommentaryNarrator(rng, stat_tracker, arc_tracker)


@pytest.fixture
def possession_narrator(pbp_narrator, color_narrator):
    return PossessionNarrator(pbp_narrator, color_narrator)


@pytest.fixture
def broadcast_mixer(possession_narrator, stat_tracker, arc_tracker):
    return BroadcastMixer(
        possession_narrator=possession_narrator,
        stat_tracker=stat_tracker,
        arc_tracker=arc_tracker,
    )


# ---------------------------------------------------------------------------
# Event creation tests
# ---------------------------------------------------------------------------


class TestNarrationEvents:
    def test_shot_result_event_fields(self):
        event = ShotResultEvent(
            shooter_name="Curry",
            shooter_id=1,
            made=True,
            points=3,
            distance=24.0,
            zone="Three Top Key",
            is_three=True,
            team_name="Warriors",
            new_score_home=50,
            new_score_away=47,
            lead=3,
        )
        assert event.event_type == NarrationEventType.SHOT_RESULT
        assert event.shooter_name == "Curry"
        assert event.made is True
        assert event.points == 3
        assert event.is_three is True

    def test_dribble_move_event(self):
        event = DribbleMoveEvent(
            player_name="Harden",
            move_type="step_back",
            success=True,
            ankle_breaker=False,
        )
        assert event.event_type == NarrationEventType.DRIBBLE_MOVE
        assert event.player_name == "Harden"
        assert event.success is True

    def test_screen_event(self):
        event = ScreenEvent(
            screener_name="Gobert",
            handler_name="Mitchell",
            pnr_coverage="drop",
        )
        assert event.event_type == NarrationEventType.SCREEN_ACTION

    def test_quarter_boundary_event(self):
        event = QuarterBoundaryEvent(
            kind=QuarterEventKind.HALFTIME,
            quarter=2,
            home_team="Celtics",
            away_team="Lakers",
            home_score=55,
            away_score=52,
        )
        assert event.kind == QuarterEventKind.HALFTIME

    def test_turnover_event_steal(self):
        event = TurnoverEvent(
            player_name="Harden",
            is_steal=True,
            stealer_name="Butler",
        )
        assert event.is_steal is True
        assert event.stealer_name == "Butler"


# ---------------------------------------------------------------------------
# Stat tracker tests
# ---------------------------------------------------------------------------


class TestStatTracker:
    def test_made_shot_tracking(self, stat_tracker):
        ctx = stat_tracker.on_made_shot(
            player_id=1, player_name="Tatum", is_home=True,
            points=3, is_three=True, game_clock=600.0,
        )
        pstats = stat_tracker.get_player(1)
        assert pstats.points == 3
        assert pstats.fg_made == 1
        assert pstats.three_made == 1
        assert stat_tracker.home_score == 3

    def test_missed_shot_tracking(self, stat_tracker):
        stat_tracker.on_missed_shot(
            player_id=1, player_name="Tatum", is_home=True, is_three=False,
        )
        pstats = stat_tracker.get_player(1)
        assert pstats.fg_attempted == 1
        assert pstats.consecutive_misses == 1

    def test_hot_streak_detection(self, stat_tracker):
        for _ in range(4):
            stat_tracker.on_made_shot(
                player_id=1, player_name="Tatum", is_home=True,
                points=2, is_three=False, game_clock=600.0,
            )
        pstats = stat_tracker.get_player(1)
        assert pstats.is_hot is True
        assert pstats.consecutive_makes == 4

    def test_cold_streak_detection(self, stat_tracker):
        for _ in range(5):
            stat_tracker.on_missed_shot(
                player_id=1, player_name="Tatum", is_home=True, is_three=False,
            )
        pstats = stat_tracker.get_player(1)
        assert pstats.is_cold is True

    def test_milestone_detection(self, stat_tracker):
        for _ in range(10):
            ctx = stat_tracker.on_made_shot(
                player_id=1, player_name="Tatum", is_home=True,
                points=2, is_three=False, game_clock=600.0,
            )
        pstats = stat_tracker.get_player(1)
        assert pstats.points == 20
        assert 20 in pstats.announced_milestones

    def test_scoring_run_tracking(self, stat_tracker):
        for _ in range(4):
            stat_tracker.on_made_shot(
                player_id=1, player_name="Tatum", is_home=True,
                points=2, is_three=False, game_clock=600.0,
            )
        assert stat_tracker.scoring_run.current_run_points == 8
        assert stat_tracker.scoring_run.is_significant_run is True

    def test_lead_change_tracking(self, stat_tracker):
        # Home scores 2 (diff: +2)
        stat_tracker.on_made_shot(1, "Tatum", True, 2, False, 700.0)
        # Away scores 2 (diff: 0, tie)
        stat_tracker.on_made_shot(2, "LeBron", False, 2, False, 690.0)
        assert stat_tracker.ties == 1
        # Away scores 3 (diff: -3, away leads)
        stat_tracker.on_made_shot(2, "LeBron", False, 3, True, 680.0)
        # Home scores 5 via back-to-back - go from -3 to +2 in one step
        # diff was -3, scoring 5 makes home=7, away=5, diff=+2
        # old_diff*new_diff = -3*2 = -6 < 0 => lead change!
        stat_tracker.on_made_shot(1, "Tatum", True, 2, False, 670.0)  # diff -1
        stat_tracker.on_made_shot(1, "Tatum", True, 3, True, 660.0)  # diff +2
        assert stat_tracker.lead_changes >= 1

    def test_player_stat_line(self):
        pstats = PlayerNarrationStats(player_id=1, player_name="Tatum")
        pstats.points = 25
        pstats.assists = 5
        pstats.rebounds = 8
        assert "25 pts" in pstats.stat_line()
        assert "5 ast" in pstats.stat_line()
        assert "8 reb" in pstats.stat_line()

    def test_shooting_line(self):
        pstats = PlayerNarrationStats(player_id=1, player_name="Tatum")
        pstats.fg_made = 8
        pstats.fg_attempted = 15
        pstats.three_made = 3
        pstats.three_attempted = 7
        assert "8-for-15" in pstats.shooting_line()
        assert "3-for-7 from three" in pstats.shooting_line()

    def test_score_string(self, stat_tracker):
        stat_tracker.on_made_shot(1, "Tatum", True, 3, True, 700.0)
        assert "Celtics 3" in stat_tracker.score_string()
        assert "Lakers 0" in stat_tracker.score_string()


# ---------------------------------------------------------------------------
# Narrative arc tests
# ---------------------------------------------------------------------------


class TestNarrativeArc:
    def test_close_game_arc(self, stat_tracker, arc_tracker):
        # Simulate a close 4th quarter game
        stat_tracker.home_score = 95
        stat_tracker.away_score = 93
        snapshot = arc_tracker.update(quarter=4, game_clock=60.0)
        assert snapshot.has_active_arc
        assert snapshot.primary_arc.arc_type == ArcType.CLOSE_GAME

    def test_blowout_arc(self, stat_tracker, arc_tracker):
        stat_tracker.home_score = 110
        stat_tracker.away_score = 85
        snapshot = arc_tracker.update(quarter=3, game_clock=300.0)
        arcs = [a for a in arc_tracker.arcs if a.arc_type == ArcType.BLOWOUT]
        assert len(arcs) > 0

    def test_star_performance_arc(self, stat_tracker, arc_tracker):
        pstats = stat_tracker.get_player(1, "Tatum")
        pstats.points = 35
        snapshot = arc_tracker.update(quarter=3, game_clock=300.0)
        arcs = [a for a in arc_tracker.arcs if a.arc_type == ArcType.STAR_PERFORMANCE]
        assert len(arcs) > 0
        assert arcs[0].team_or_player == "Tatum"

    def test_no_active_arc_early_game(self, stat_tracker, arc_tracker):
        stat_tracker.home_score = 10
        stat_tracker.away_score = 8
        snapshot = arc_tracker.update(quarter=1, game_clock=400.0)
        # May or may not have an arc, but shouldn't be blowout/comeback
        blowouts = [a for a in arc_tracker.arcs if a.arc_type == ArcType.BLOWOUT]
        assert len(blowouts) == 0


# ---------------------------------------------------------------------------
# Play-by-play narrator tests
# ---------------------------------------------------------------------------


class TestPlayByPlay:
    def test_narrate_made_three(self, pbp_narrator):
        event = ShotResultEvent(
            shooter_name="Curry",
            shooter_id=1,
            made=True,
            points=3,
            distance=24.0,
            zone="Three Top Key",
            is_three=True,
            team_name="Warriors",
            new_score_home=50,
            new_score_away=47,
            lead=3,
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert len(text) > 0
        assert "Curry" in text

    def test_narrate_missed_shot(self, pbp_narrator):
        event = ShotResultEvent(
            shooter_name="Westbrook",
            shooter_id=2,
            made=False,
            distance=18.0,
            zone="Mid Range",
            is_three=False,
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Westbrook" in text

    def test_narrate_dribble_move(self, pbp_narrator):
        event = DribbleMoveEvent(
            player_name="Harden",
            move_type="step_back",
            success=True,
            defender_name="Holiday",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Harden" in text

    def test_narrate_ankle_breaker(self, pbp_narrator):
        event = DribbleMoveEvent(
            player_name="Kyrie",
            move_type="crossover",
            success=True,
            ankle_breaker=True,
            defender_name="Smart",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "ANKLE BREAKER" in text

    def test_narrate_screen(self, pbp_narrator):
        event = ScreenEvent(
            screener_name="Gobert",
            handler_name="Mitchell",
            pnr_coverage="drop",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Gobert" in text

    def test_narrate_pass(self, pbp_narrator):
        event = PassEvent(
            passer_name="LeBron",
            receiver_name="Davis",
            pass_type="chest",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None

    def test_narrate_turnover_steal(self, pbp_narrator):
        event = TurnoverEvent(
            player_name="Harden",
            is_steal=True,
            stealer_name="Butler",
            team_name="76ers",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Butler" in text

    def test_narrate_block(self, pbp_narrator):
        event = BlockEvent(
            blocker_name="Gobert",
            shooter_name="Tatum",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Gobert" in text

    def test_narrate_rebound(self, pbp_narrator):
        event = ReboundEvent(
            rebounder_name="Davis",
            is_offensive=False,
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Davis" in text

    def test_narrate_offensive_rebound(self, pbp_narrator):
        event = ReboundEvent(
            rebounder_name="Davis",
            is_offensive=True,
        )
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "offensive" in text.lower()

    def test_narrate_free_throw(self, pbp_narrator):
        made = FreeThrowEvent(shooter_name="Giannis", made=True)
        missed = FreeThrowEvent(shooter_name="Giannis", made=False)
        assert pbp_narrator.narrate(made) is not None
        assert pbp_narrator.narrate(missed) is not None

    def test_narrate_timeout(self, pbp_narrator):
        event = TimeoutEvent(team_name="Celtics", timeouts_remaining=4)
        text = pbp_narrator.narrate(event)
        assert text is not None
        assert "Celtics" in text

    def test_narrate_substitution(self, pbp_narrator):
        event = SubstitutionEvent(
            player_in_name="White",
            player_out_name="Smart",
            team_name="Celtics",
        )
        text = pbp_narrator.narrate(event)
        assert text is not None

    def test_narrate_quarter_end(self, pbp_narrator):
        event = QuarterBoundaryEvent(
            kind=QuarterEventKind.QUARTER_END,
            quarter=1,
            home_team="Celtics",
            away_team="Lakers",
            home_score=28,
            away_score=25,
        )
        text = pbp_narrator.narrate(event)
        assert text is not None

    def test_template_non_repetition(self, pbp_narrator):
        """Templates should not repeat within a short window."""
        texts = set()
        for i in range(5):
            event = ShotResultEvent(
                shooter_name=f"Player{i}",
                shooter_id=i,
                made=True,
                points=3,
                distance=24.0,
                zone="Three Top Key",
                is_three=True,
                team_name="Team",
                new_score_home=50 + i * 3,
                new_score_away=47,
                lead=3 + i * 3,
            )
            text = pbp_narrator.narrate(event)
            texts.add(text)
        # Should have some variety (at least 3 unique out of 5)
        assert len(texts) >= 3


# ---------------------------------------------------------------------------
# Possession narrator tests
# ---------------------------------------------------------------------------


class TestPossessionNarrator:
    def test_compose_simple_possession(self, possession_narrator):
        from hoops_sim.narration.narrative_arc import ArcSnapshot

        possession_narrator.start_possession()
        possession_narrator.add_event(BallAdvanceEvent(
            ball_handler_name="Tatum",
        ))
        possession_narrator.add_event(ShotResultEvent(
            shooter_name="Tatum",
            made=True,
            points=2,
            distance=15.0,
            zone="Mid Range",
            team_name="Celtics",
            new_score_home=50,
            new_score_away=48,
            lead=2,
        ))
        narration = possession_narrator.compose(ArcSnapshot())
        assert narration.has_content
        assert len(narration.pbp_lines) > 0

    def test_compose_with_dribble_and_shot(self, possession_narrator):
        from hoops_sim.narration.narrative_arc import ArcSnapshot

        possession_narrator.start_possession()
        possession_narrator.add_event(DribbleMoveEvent(
            player_name="Harden",
            move_type="step_back",
            success=True,
            defender_name="Holiday",
        ))
        possession_narrator.add_event(ShotResultEvent(
            shooter_name="Harden",
            made=True,
            points=3,
            distance=25.0,
            zone="Three Top Key",
            is_three=True,
            team_name="Rockets",
            new_score_home=40,
            new_score_away=38,
            lead=2,
        ))
        narration = possession_narrator.compose(ArcSnapshot())
        assert narration.has_content
        full_text = narration.full_text()
        assert "Harden" in full_text

    def test_tagged_text_format(self, possession_narrator):
        from hoops_sim.narration.narrative_arc import ArcSnapshot

        possession_narrator.start_possession()
        possession_narrator.add_event(ShotResultEvent(
            shooter_name="Curry",
            made=True,
            points=3,
            distance=28.0,
            zone="Three Top Key",
            is_three=True,
            team_name="Warriors",
            new_score_home=60,
            new_score_away=55,
            lead=5,
        ))
        narration = possession_narrator.compose(ArcSnapshot())
        tagged = narration.tagged_text()
        assert "[PBP]" in tagged


# ---------------------------------------------------------------------------
# Broadcast mixer tests
# ---------------------------------------------------------------------------


class TestBroadcastMixer:
    def test_full_possession_produces_output(self, broadcast_mixer):
        broadcast_mixer.start_possession(quarter=1, game_clock=700.0)
        broadcast_mixer.add_event(ShotResultEvent(
            shooter_name="Tatum",
            made=True,
            points=2,
            distance=10.0,
            zone="Mid Range",
            team_name="Celtics",
            new_score_home=50,
            new_score_away=48,
            lead=2,
        ))
        lines = broadcast_mixer.end_possession()
        assert len(lines) > 0
        assert all(isinstance(l, BroadcastLine) for l in lines)

    def test_score_header(self, broadcast_mixer, stat_tracker):
        stat_tracker.home_score = 55
        stat_tracker.away_score = 52
        broadcast_mixer._current_quarter = 2
        broadcast_mixer._current_clock = 360.0
        header = broadcast_mixer.score_header("Celtics", "Lakers")
        assert "Celtics" in header
        assert "55" in header
        assert "52" in header

    def test_highlights_mode_filters(self, possession_narrator, stat_tracker, arc_tracker):
        mixer = BroadcastMixer(
            possession_narrator=possession_narrator,
            stat_tracker=stat_tracker,
            arc_tracker=arc_tracker,
            verbosity=VerbosityLevel.HIGHLIGHTS_ONLY,
        )
        mixer.start_possession(quarter=1, game_clock=700.0)
        mixer.add_event(ShotResultEvent(
            shooter_name="Tatum",
            made=True,
            points=2,
            distance=10.0,
            zone="Close",
            team_name="Celtics",
            new_score_home=50,
            new_score_away=48,
            lead=2,
        ))
        lines = mixer.end_possession()
        # In highlights mode, low-intensity plays may be filtered
        # (all lines should have intensity >= 0.7 if present)
        for line in lines:
            assert line.intensity >= 0.7 or line.voice == "color"


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------


class TestFormatter:
    def test_format_lines(self, stat_tracker):
        formatter = BroadcastFormatter(
            home_team="Celtics",
            away_team="Lakers",
            stat_tracker=stat_tracker,
        )
        lines = [
            BroadcastLine(text="Tatum pulls up... GOT IT!", voice="pbp", quarter=1),
            BroadcastLine(text="He's 5-for-8 tonight.", voice="color", quarter=1),
        ]
        output = formatter.format_lines(lines)
        assert "[PBP]" in output
        assert "[COLOR]" in output
        assert "Tatum" in output

    def test_box_score_summary(self, stat_tracker):
        stat_tracker.home_score = 108
        stat_tracker.away_score = 102
        pstats = stat_tracker.get_player(1, "Tatum")
        pstats.points = 30
        pstats.assists = 5
        pstats.rebounds = 8

        formatter = BroadcastFormatter(
            home_team="Celtics",
            away_team="Lakers",
            stat_tracker=stat_tracker,
        )
        summary = formatter.format_box_score_summary()
        assert "FINAL" in summary
        assert "108" in summary
        assert "Tatum" in summary
        assert "30 pts" in summary


# ---------------------------------------------------------------------------
# Calibration target tests
# ---------------------------------------------------------------------------


class TestCalibrationTargets:
    def test_words_per_possession_check(self):
        result = NarrationCalibrationResult(
            total_possessions=100,
            total_words=5000,
        )
        assert result.words_per_possession == 50.0
        issues = result.check_targets()
        # Should not flag words per possession
        wpp_issues = [i for i in issues if "Words per possession" in i]
        assert len(wpp_issues) == 0

    def test_low_coverage_flagged(self):
        result = NarrationCalibrationResult(
            total_possessions=100,
            possessions_with_narration=50,
            total_words=2000,
        )
        issues = result.check_targets()
        coverage_issues = [i for i in issues if "coverage" in i.lower()]
        assert len(coverage_issues) > 0

    def test_summary_format(self):
        result = NarrationCalibrationResult(
            total_possessions=100,
            total_words=5000,
            total_pbp_lines=150,
            total_color_lines=40,
            possessions_with_narration=95,
            possessions_with_color=30,
        )
        summary = result.summary()
        assert "Narration Calibration Report" in summary
        assert "100" in summary


# ---------------------------------------------------------------------------
# Integration: simulator produces broadcast output
# ---------------------------------------------------------------------------


class TestBroadcastIntegration:
    def test_simulator_populates_broadcast_mixer(self, home_team, away_team):
        """A simulated game should produce broadcast output."""
        from hoops_sim.engine.simulator import GameSimulator

        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=True,
        )
        assert sim.broadcast_mixer is not None
        assert sim.broadcast_stats is not None

        result = sim.simulate_full_game()
        # The broadcast mixer should have produced output
        assert len(sim.broadcast_mixer.all_output) > 0

        # Broadcast stats should track scores
        assert sim.broadcast_stats.home_score > 0 or sim.broadcast_stats.away_score > 0

    def test_simulator_without_narration_skips_broadcast(self, home_team, away_team):
        from hoops_sim.engine.simulator import GameSimulator

        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=42,
            narrate=False,
        )
        assert sim.broadcast_mixer is None
        assert sim.broadcast_stats is None
        result = sim.simulate_full_game()
        assert result.home_score > 0 or result.away_score > 0


# Create team fixtures matching the simulator test module pattern
@pytest.fixture
def home_team():
    from hoops_sim.data.generator import generate_roster
    from hoops_sim.models.team import Team
    rng_obj = SeededRNG(100)
    roster = generate_roster(rng_obj)
    return Team(
        id=1, city="Boston", name="Celtics", abbreviation="CEL",
        conference="East", division="Atlantic", roster=roster,
    )


@pytest.fixture
def away_team():
    from hoops_sim.data.generator import generate_roster
    from hoops_sim.models.team import Team
    rng_obj = SeededRNG(200)
    roster = generate_roster(rng_obj)
    return Team(
        id=2, city="Los Angeles", name="Lakers", abbreviation="LAK",
        conference="West", division="Pacific", roster=roster,
    )
