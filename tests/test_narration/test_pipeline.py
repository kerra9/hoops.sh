"""End-to-end tests for the v2 narration pipeline.

Covers all seven layers, cross-cutting systems, and integration with
the existing event types. Tests structural properties and validates
that the pipeline produces broadcast-quality prose.
"""

from __future__ import annotations

import pytest

from hoops_sim.narration.anti_repetition import (
    AntiRepetitionSystem,
    RhythmTracker,
    SentenceShape,
    StructureTracker,
    ThematicTracker,
    VocabularyTracker,
)
from hoops_sim.narration.characters import (
    CharacterCast,
    DefenderState,
    PlayerVocabulary,
)
from hoops_sim.narration.clause_banks import intensity_band
from hoops_sim.narration.clause_banks.defense import dignity_band, get_defender_clauses
from hoops_sim.narration.clause_banks.dribble import get_dribble_clauses
from hoops_sim.narration.clause_banks.drive import get_drive_clauses
from hoops_sim.narration.clause_banks.pass_ import get_pass_clauses
from hoops_sim.narration.clause_banks.reaction import get_announcer_reactions
from hoops_sim.narration.clause_banks.screen import get_screen_clauses
from hoops_sim.narration.clause_banks.setup import get_setup_clauses
from hoops_sim.narration.clause_banks.shot import get_shot_clauses
from hoops_sim.narration.clause_gen import DefaultClauseGenerator
from hoops_sim.narration.dramaturgy import DefaultDramaturg
from hoops_sim.narration.enrichment import DefaultEventEnricher
from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    PassEvent,
    ReboundEvent,
    ScreenEvent,
    ShotResultEvent,
    TurnoverEvent,
)
from hoops_sim.narration.grammar import DefaultGrammarEngine, SubjectTracker
from hoops_sim.narration.pipeline import NarrationPipeline
from hoops_sim.narration.prose_renderer import DefaultProseRenderer
from hoops_sim.narration.registry import Registry
from hoops_sim.narration.sequence_recognizer import DefaultSequenceRecognizer
from hoops_sim.narration.types import (
    Clause,
    DramaticBeat,
    DramaticPlan,
    DramaticRole,
    EnrichedEvent,
    GameContext,
    GrammarClause,
    SequenceTag,
    StyledClause,
)
from hoops_sim.narration.voice import AnnouncerProfile, DefaultVoiceStyler
from hoops_sim.narration.voices import (
    VOICE_PROFILES,
    classic_profile,
    hype_profile,
)
from hoops_sim.utils.rng import SeededRNG


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rng():
    return SeededRNG(42)


@pytest.fixture
def pipeline(rng):
    return NarrationPipeline(rng=rng)


@pytest.fixture
def context():
    return GameContext(
        quarter=2,
        game_clock=300.0,
        shot_clock=18.0,
        home_score=45,
        away_score=42,
        home_team="Hawks",
        away_team="Celtics",
    )


@pytest.fixture
def clutch_context():
    return GameContext(
        quarter=4,
        game_clock=30.0,
        shot_clock=14.0,
        home_score=98,
        away_score=97,
        home_team="Hawks",
        away_team="Celtics",
    )


def _harden_ankle_breaker_events() -> list:
    """The signature example from the plan: Harden ankle-breaker three."""
    return [
        BallAdvanceEvent(ball_handler_name="Harden"),
        DribbleMoveEvent(
            player_name="Harden",
            move_type="jab_step",
            defender_name="Holiday",
        ),
        DribbleMoveEvent(
            player_name="Harden",
            move_type="crossover",
            defender_name="Holiday",
            separation_gained=0.3,
        ),
        DriveEvent(
            driver_name="Harden",
            defender_name="Holiday",
        ),
        DribbleMoveEvent(
            player_name="Harden",
            move_type="behind_the_back_snatchback",
            ankle_breaker=True,
            defender_name="Holiday",
            separation_gained=0.8,
        ),
        ShotResultEvent(
            shooter_name="Harden",
            made=True,
            points=3,
            distance=26.0,
            zone="three_top",
            is_three=True,
        ),
    ]


def _simple_catch_and_shoot() -> list:
    """Simple catch and shoot possession."""
    return [
        BallAdvanceEvent(ball_handler_name="Mitchell"),
        PassEvent(
            passer_name="Mitchell",
            receiver_name="Thompson",
            pass_type="swing",
            is_kick_out=False,
        ),
        ShotResultEvent(
            shooter_name="Thompson",
            made=True,
            points=3,
            is_three=True,
            zone="three_left_corner",
        ),
    ]


def _fast_break_dunk() -> list:
    """Fast break ending in a dunk."""
    return [
        BallAdvanceEvent(
            ball_handler_name="James",
            is_transition=True,
        ),
        DriveEvent(
            driver_name="James",
            defender_name="Williams",
        ),
        ShotResultEvent(
            shooter_name="James",
            made=True,
            points=2,
            is_dunk=True,
        ),
    ]


# ---------------------------------------------------------------------------
# Layer 1: Event Enrichment
# ---------------------------------------------------------------------------


class TestEventEnrichment:
    def test_enriches_all_events(self, context):
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        assert len(enriched) == len(events)
        for ee in enriched:
            assert isinstance(ee, EnrichedEvent)
            assert ee.raw is not None

    def test_extracts_player_names(self, context):
        enricher = DefaultEventEnricher()
        event = DribbleMoveEvent(
            player_name="Harden",
            defender_name="Holiday",
            move_type="crossover",
        )
        ee = enricher.enrich(event, context)
        assert ee.player_name == "Harden"
        assert ee.defender_name == "Holiday"

    def test_detects_signature_move(self, context):
        enricher = DefaultEventEnricher()
        event = DribbleMoveEvent(
            player_name="Harden",
            move_type="crossover",
            ankle_breaker=True,
        )
        ee = enricher.enrich(event, context)
        assert ee.is_signature_move is True

    def test_computes_crowd_energy_close_game(self):
        enricher = DefaultEventEnricher()
        ctx = GameContext(
            quarter=4, game_clock=60.0, home_score=98, away_score=97,
        )
        event = BallAdvanceEvent(ball_handler_name="Harden")
        ee = enricher.enrich(event, ctx)
        assert ee.crowd_energy > 0.7

    def test_builds_clock_context_clutch(self):
        enricher = DefaultEventEnricher()
        ctx = GameContext(
            quarter=4, game_clock=30.0, home_score=98, away_score=97,
        )
        event = BallAdvanceEvent(ball_handler_name="Harden")
        ee = enricher.enrich(event, ctx)
        assert ee.clock_context is not None
        assert "remaining" in ee.clock_context

    def test_no_crash_on_empty_names(self, context):
        enricher = DefaultEventEnricher()
        event = BallAdvanceEvent()
        ee = enricher.enrich(event, context)
        assert ee.player_name == ""


# ---------------------------------------------------------------------------
# Layer 2: Sequence Recognition
# ---------------------------------------------------------------------------


class TestSequenceRecognition:
    def test_recognizes_isolation(self, context):
        recognizer = DefaultSequenceRecognizer()
        enricher = DefaultEventEnricher()
        events = [
            BallAdvanceEvent(ball_handler_name="Harden"),
            DribbleMoveEvent(
                player_name="Harden", move_type="crossover",
                defender_name="Holiday",
            ),
            DribbleMoveEvent(
                player_name="Harden", move_type="step_back",
                defender_name="Holiday",
            ),
            ShotResultEvent(shooter_name="Harden", made=True, points=2),
        ]
        enriched = [enricher.enrich(e, context) for e in events]
        tag = recognizer.recognize(enriched)
        assert tag.primary == "isolation"
        assert tag.confidence > 0.5

    def test_recognizes_fast_break(self, context):
        recognizer = DefaultSequenceRecognizer()
        enricher = DefaultEventEnricher()
        events = _fast_break_dunk()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = recognizer.recognize(enriched)
        assert tag.primary == "fast_break"
        assert tag.tempo == "fast"

    def test_recognizes_pick_and_roll(self, context):
        recognizer = DefaultSequenceRecognizer()
        enricher = DefaultEventEnricher()
        events = [
            BallAdvanceEvent(ball_handler_name="Trae"),
            ScreenEvent(
                handler_name="Trae", screener_name="Collins",
                screen_type="ball_screen",
            ),
            DriveEvent(driver_name="Trae", defender_name="Smart"),
            ShotResultEvent(shooter_name="Trae", made=True, points=2),
        ]
        enriched = [enricher.enrich(e, context) for e in events]
        tag = recognizer.recognize(enriched)
        assert tag.primary == "pick_and_roll"

    def test_recognizes_catch_and_shoot(self, context):
        recognizer = DefaultSequenceRecognizer()
        enricher = DefaultEventEnricher()
        events = _simple_catch_and_shoot()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = recognizer.recognize(enriched)
        assert tag.primary == "catch_and_shoot"

    def test_empty_events_returns_generic(self):
        recognizer = DefaultSequenceRecognizer()
        tag = recognizer.recognize([])
        assert tag.primary == "generic"

    def test_confidence_between_0_and_1(self, context):
        recognizer = DefaultSequenceRecognizer()
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = recognizer.recognize(enriched)
        assert 0.0 <= tag.confidence <= 1.0


# ---------------------------------------------------------------------------
# Layer 3: Possession Dramaturgy
# ---------------------------------------------------------------------------


class TestDramaturgy:
    def test_every_plan_has_climax(self, context):
        dramaturg = DefaultDramaturg()
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = SequenceTag(primary="isolation")
        plan = dramaturg.plan(enriched, tag, context)

        roles = [b.role for b in plan.beats]
        assert DramaticRole.CLIMAX in roles

    def test_intensity_reaches_peak_at_climax(self, context):
        dramaturg = DefaultDramaturg()
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = SequenceTag(primary="isolation")
        plan = dramaturg.plan(enriched, tag, context)

        climax_intensities = [
            b.intensity for b in plan.beats
            if b.role == DramaticRole.CLIMAX
        ]
        assert any(i >= 0.7 for i in climax_intensities)

    def test_defender_dignity_degrades(self, context):
        dramaturg = DefaultDramaturg()
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = SequenceTag(primary="isolation")
        plan = dramaturg.plan(enriched, tag, context)

        dignities = [b.defender_dignity for b in plan.beats]
        # Dignity should decrease over the possession
        assert dignities[-1] < dignities[0]

    def test_clutch_context_boosts_intensity(self, clutch_context):
        dramaturg = DefaultDramaturg()
        enricher = DefaultEventEnricher()
        events = [
            BallAdvanceEvent(ball_handler_name="Harden"),
            ShotResultEvent(
                shooter_name="Harden", made=True, points=3,
                is_three=True,
            ),
        ]
        enriched = [enricher.enrich(e, clutch_context) for e in events]
        tag = SequenceTag(primary="generic")
        plan = dramaturg.plan(enriched, tag, clutch_context)
        assert plan.peak_intensity > 0.8

    def test_empty_events_returns_empty_plan(self, context):
        dramaturg = DefaultDramaturg()
        tag = SequenceTag()
        plan = dramaturg.plan([], tag, context)
        assert len(plan.beats) == 0


# ---------------------------------------------------------------------------
# Layer 4: Clause Generation
# ---------------------------------------------------------------------------


class TestClauseGeneration:
    def test_every_beat_produces_clauses(self, rng, context):
        generator = DefaultClauseGenerator()
        enricher = DefaultEventEnricher()
        dramaturg = DefaultDramaturg()

        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = SequenceTag(primary="isolation")
        plan = dramaturg.plan(enriched, tag, context)

        for beat in plan.beats:
            clauses = generator.generate(beat, plan, rng)
            assert len(clauses) >= 1
            assert all(c.text for c in clauses)

    def test_ankle_breaker_generates_multiple_clauses(self, rng, context):
        generator = DefaultClauseGenerator()
        enricher = DefaultEventEnricher()
        dramaturg = DefaultDramaturg()

        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        tag = SequenceTag(primary="isolation")
        plan = dramaturg.plan(enriched, tag, context)

        # Find the ankle breaker beat
        for beat in plan.beats:
            raw = beat.event.raw
            if isinstance(raw, DribbleMoveEvent) and raw.ankle_breaker:
                clauses = generator.generate(beat, plan, rng)
                # Should produce handler clause + defender clause at minimum
                assert len(clauses) >= 2
                has_defender = any(c.is_defender_clause for c in clauses)
                assert has_defender
                break

    def test_shot_result_generates_reaction(self, rng, context):
        generator = DefaultClauseGenerator()
        beat = DramaticBeat(
            event=EnrichedEvent(
                raw=ShotResultEvent(
                    shooter_name="Harden", made=True, points=3,
                    is_three=True,
                ),
                player_name="Harden",
            ),
            role=DramaticRole.CLIMAX,
            intensity=0.9,
        )
        plan = DramaticPlan(beats=[beat])
        clauses = generator.generate(beat, plan, rng)
        assert len(clauses) >= 1
        has_reaction = any(c.is_reaction for c in clauses)
        assert has_reaction  # high-intensity makes should have announcer reaction

    def test_no_empty_clause_text(self, rng, context):
        generator = DefaultClauseGenerator()
        enricher = DefaultEventEnricher()
        dramaturg = DefaultDramaturg()

        for events_fn in [
            _harden_ankle_breaker_events,
            _simple_catch_and_shoot,
            _fast_break_dunk,
        ]:
            events = events_fn()
            enriched = [enricher.enrich(e, context) for e in events]
            tag = SequenceTag()
            plan = dramaturg.plan(enriched, tag, context)
            for beat in plan.beats:
                clauses = generator.generate(beat, plan, rng)
                for c in clauses:
                    assert c.text, f"Empty clause for {beat.event.raw}"


# ---------------------------------------------------------------------------
# Layer 5: Grammar Engine
# ---------------------------------------------------------------------------


class TestGrammarEngine:
    def test_subject_elision(self, rng):
        engine = DefaultGrammarEngine(rng=rng)
        clauses = [
            Clause(
                text="brings the ball up",
                subject="Harden",
                role=DramaticRole.ESTABLISH,
                intensity=0.2,
            ),
            Clause(
                text="jab step, sizes up Holiday",
                subject="Harden",
                role=DramaticRole.BUILD,
                intensity=0.3,
            ),
            Clause(
                text="crossover, gets a step",
                subject="Harden",
                role=DramaticRole.BUILD,
                intensity=0.4,
            ),
        ]
        plan = DramaticPlan()
        result = engine.process(clauses, plan)
        assert len(result) == 3
        # First clause should have subject
        assert "Harden" in result[0].text
        # Subsequent same-subject clauses should NOT have subject
        assert "Harden" not in result[1].text
        assert "Harden" not in result[2].text

    def test_subject_switch_restates(self, rng):
        engine = DefaultGrammarEngine(rng=rng)
        clauses = [
            Clause(
                text="drives to the left",
                subject="Harden",
                role=DramaticRole.BUILD,
                intensity=0.5,
            ),
            Clause(
                text="struggles to keep up",
                subject="Holiday",
                subject_type="defender",
                role=DramaticRole.BUILD,
                intensity=0.5,
                is_defender_clause=True,
            ),
        ]
        plan = DramaticPlan()
        result = engine.process(clauses, plan)
        assert "Holiday" in result[1].text

    def test_high_intensity_caps(self, rng):
        engine = DefaultGrammarEngine(rng=rng)
        clauses = [
            Clause(
                text="DRAINS THE THREE",
                subject="Harden",
                role=DramaticRole.CLIMAX,
                intensity=0.9,
            ),
        ]
        plan = DramaticPlan()
        result = engine.process(clauses, plan)
        assert result[0].capitalization == "upper"

    def test_no_double_punctuation(self, rng):
        engine = DefaultGrammarEngine(rng=rng)
        clauses = [
            Clause(
                text="BANG!",
                subject=None,
                subject_type="announcer",
                role=DramaticRole.CLIMAX,
                intensity=0.9,
                is_reaction=True,
            ),
        ]
        plan = DramaticPlan()
        result = engine.process(clauses, plan)
        text = result[0].text + result[0].terminal_punctuation
        assert ".." not in text


# ---------------------------------------------------------------------------
# Layer 6: Voice and Style
# ---------------------------------------------------------------------------


class TestVoiceAndStyle:
    def test_classic_profile_exists(self):
        profile = classic_profile()
        assert profile.name == "Classic"
        assert profile.caps_threshold == 0.85

    def test_hype_profile_has_lower_caps_threshold(self):
        profile = hype_profile()
        assert profile.caps_threshold < 0.85

    def test_all_profiles_loadable(self):
        for name, factory in VOICE_PROFILES.items():
            profile = factory()
            assert profile.name
            assert 0.0 <= profile.caps_threshold <= 1.0

    def test_voice_styler_produces_styled_clauses(self, rng):
        styler = DefaultVoiceStyler(rng=rng)
        gcs = [
            GrammarClause(
                text="Harden drains the three",
                connector="",
                capitalization="sentence",
                terminal_punctuation="!",
            ),
        ]
        plan = DramaticPlan(peak_intensity=0.8)
        result = styler.style(gcs, plan)
        assert len(result) >= 1
        assert result[0].text[0].isupper()


# ---------------------------------------------------------------------------
# Layer 7: Prose Rendering
# ---------------------------------------------------------------------------


class TestProseRendering:
    def test_produces_non_empty_output(self):
        renderer = DefaultProseRenderer()
        clauses = [
            StyledClause(
                text="Harden brings the ball up",
                connector="",
                terminal=".",
            ),
        ]
        result = renderer.render(clauses)
        assert len(result) > 0
        assert result == result.strip()

    def test_no_orphan_punctuation(self):
        renderer = DefaultProseRenderer()
        clauses = [
            StyledClause(text="drives left", connector="", terminal=""),
            StyledClause(text="DRAINS IT", connector="! ", is_caps=True, terminal="!"),
        ]
        result = renderer.render(clauses)
        assert ".." not in result
        assert "!." not in result

    def test_ends_with_punctuation(self):
        renderer = DefaultProseRenderer()
        clauses = [
            StyledClause(text="nice play", connector=""),
        ]
        result = renderer.render(clauses)
        assert result[-1] in ".!?"

    def test_capitalizes_first_clause(self):
        renderer = DefaultProseRenderer()
        clauses = [
            StyledClause(text="harden brings it up", connector=""),
        ]
        result = renderer.render(clauses)
        assert result[0].isupper()


# ---------------------------------------------------------------------------
# Cross-cutting: Anti-Repetition
# ---------------------------------------------------------------------------


class TestAntiRepetition:
    def test_vocabulary_tracker_freshness(self):
        tracker = VocabularyTracker(window=5)
        tracker.record("drives left")
        assert not tracker.is_fresh("drives left")
        assert tracker.is_fresh("drives right")

    def test_vocabulary_tracker_window(self):
        tracker = VocabularyTracker(window=3)
        tracker.record("a")
        tracker.record("b")
        tracker.record("c")
        tracker.record("d")
        # "a" should have fallen off the window
        assert tracker.is_fresh("a")

    def test_filter_fresh_returns_all_when_none_fresh(self):
        tracker = VocabularyTracker(window=10)
        options = ["a", "b"]
        tracker.record("a")
        tracker.record("b")
        result = tracker.filter_fresh(options)
        assert len(result) == 2  # fallback to all

    def test_structure_tracker_detects_repetitive(self):
        tracker = StructureTracker(window=5)
        shape = SentenceShape(clause_count=3, connector_pattern="comma-ellipsis-bang")
        tracker.record(shape)
        tracker.record(shape)
        tracker.record(shape)
        assert tracker.is_repetitive(shape)

    def test_rhythm_tracker_suggests_short_after_long(self):
        tracker = RhythmTracker()
        tracker.record(70)
        tracker.record(65)
        assert tracker.suggest_length() == "short"

    def test_thematic_tracker_cooldown(self):
        tracker = ThematicTracker()
        assert tracker.can_use("ankle_breaker")
        tracker.record_use("ankle_breaker")
        assert not tracker.can_use("ankle_breaker")
        for _ in range(10):
            tracker.tick()
        assert tracker.can_use("ankle_breaker")

    def test_combined_system_records(self):
        system = AntiRepetitionSystem()
        system.record_possession(
            clause_texts=["drives left", "BANG!"],
            word_count=25,
            shape=SentenceShape(clause_count=2),
            themes=["ankle_breaker"],
        )
        assert not system.vocabulary.is_fresh("drives left")
        assert not system.thematic.can_use("ankle_breaker")


# ---------------------------------------------------------------------------
# Cross-cutting: Character System
# ---------------------------------------------------------------------------


class TestCharacterSystem:
    def test_defender_dignity_degrades_on_move(self):
        state = DefenderState(name="Holiday")
        assert state.dignity == 1.0
        state.on_move_beaten(separation=0.3, ankle_breaker=False)
        assert state.dignity < 1.0

    def test_defender_dignity_collapses_on_ankle_breaker(self):
        state = DefenderState(name="Holiday")
        state.on_move_beaten(separation=0.8, ankle_breaker=True)
        assert state.dignity < 0.3
        assert state.is_on_ground

    def test_player_vocabulary_for_styles(self):
        explosive = PlayerVocabulary.for_play_style("explosive")
        assert "explodes" in explosive.movement_verbs

        crafty = PlayerVocabulary.for_play_style("crafty")
        assert "glides" in crafty.movement_verbs

    def test_character_cast_from_events(self, context):
        enricher = DefaultEventEnricher()
        events = _harden_ankle_breaker_events()
        enriched = [enricher.enrich(e, context) for e in events]
        cast = CharacterCast.from_events(enriched)
        assert cast.handler == "Harden"
        assert cast.defender == "Holiday"


# ---------------------------------------------------------------------------
# Clause Banks
# ---------------------------------------------------------------------------


class TestClauseBanks:
    def test_intensity_band_mapping(self):
        assert intensity_band(0.1) == "calm"
        assert intensity_band(0.4) == "building"
        assert intensity_band(0.7) == "hype"
        assert intensity_band(0.9) == "screaming"

    def test_dribble_banks_non_empty(self):
        for move_type in ["crossover", "hesitation", "step_back",
                          "behind_the_back", "spin_move"]:
            for band in ["calm", "building", "hype", "screaming"]:
                clauses = get_dribble_clauses(move_type, band)
                assert len(clauses) >= 4, f"Too few for {move_type}/{band}"

    def test_shot_banks_non_empty(self):
        for made in [True, False]:
            for is_three in [True, False]:
                for band in ["calm", "building", "hype", "screaming"]:
                    clauses = get_shot_clauses(made, is_three, False, band)
                    assert len(clauses) >= 4

    def test_dunk_banks_non_empty(self):
        for band in ["calm", "building", "hype", "screaming"]:
            clauses = get_shot_clauses(True, False, True, band)
            assert len(clauses) >= 4

    def test_drive_banks_non_empty(self):
        for band in ["calm", "building", "hype", "screaming"]:
            clauses = get_drive_clauses(band)
            assert len(clauses) >= 4

    def test_setup_banks_non_empty(self):
        for band in ["calm", "building", "hype", "screaming"]:
            clauses = get_setup_clauses("walk_it_up", band)
            assert len(clauses) >= 4

    def test_defender_dignity_banks(self):
        for dignity in [0.9, 0.7, 0.5, 0.3, 0.1]:
            clauses = get_defender_clauses(dignity)
            assert len(clauses) >= 4

    def test_dignity_band_mapping(self):
        assert dignity_band(0.9) == "composed"
        assert dignity_band(0.7) == "reaching"
        assert dignity_band(0.5) == "struggling"
        assert dignity_band(0.3) == "stumbling"
        assert dignity_band(0.1) == "destroyed"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_register_and_get(self):
        reg: Registry = Registry("test")
        reg.register_instance("foo", "bar")
        assert reg.get("foo") == "bar"

    def test_missing_key_raises(self):
        reg: Registry = Registry("test")
        with pytest.raises(KeyError):
            reg.get("missing")

    def test_decorator_registration(self):
        reg: Registry = Registry("test")

        @reg.register("my_thing")
        class MyThing:
            pass

        assert reg.get("my_thing") is MyThing

    def test_override(self):
        reg: Registry = Registry("test")
        reg.register_instance("key", "old")
        reg.override("key", "new")
        assert reg.get("key") == "new"

    def test_keys_and_len(self):
        reg: Registry = Registry("test")
        reg.register_instance("a", 1)
        reg.register_instance("b", 2)
        assert "a" in reg.keys()
        assert len(reg) == 2


# ---------------------------------------------------------------------------
# End-to-end Pipeline Tests
# ---------------------------------------------------------------------------


class TestPipelineEndToEnd:
    def test_harden_ankle_breaker(self, pipeline, context):
        """The signature example from the plan."""
        events = _harden_ankle_breaker_events()
        output = pipeline.narrate(events, context)

        assert len(output) > 0
        assert "Harden" in output
        # Holiday should be mentioned (defender narration)
        assert "Holiday" in output or "holiday" in output.lower()
        # Should have exclamation marks (high intensity)
        assert "!" in output
        # Should have some CAPS for high-intensity moments
        has_caps = any(
            word.isupper() and len(word) > 2
            for word in output.split()
        )
        assert has_caps

    def test_catch_and_shoot(self, pipeline, context):
        events = _simple_catch_and_shoot()
        output = pipeline.narrate(events, context)
        assert len(output) > 0
        # Should mention either Mitchell or Thompson
        assert "Mitchell" in output or "Thompson" in output

    def test_fast_break_dunk(self, pipeline, context):
        events = _fast_break_dunk()
        output = pipeline.narrate(events, context)
        assert len(output) > 0
        assert "James" in output or "james" in output.lower()

    def test_empty_events_returns_empty(self, pipeline, context):
        output = pipeline.narrate([], context)
        assert output == ""

    def test_single_event(self, pipeline, context):
        events = [ShotResultEvent(
            shooter_name="Curry", made=True, points=3, is_three=True,
        )]
        output = pipeline.narrate(events, context)
        assert len(output) > 0

    def test_output_no_leading_trailing_whitespace(self, pipeline, context):
        events = _harden_ankle_breaker_events()
        output = pipeline.narrate(events, context)
        assert output == output.strip()

    def test_output_ends_with_punctuation(self, pipeline, context):
        events = _harden_ankle_breaker_events()
        output = pipeline.narrate(events, context)
        assert output[-1] in ".!?"

    def test_clutch_context_produces_higher_intensity(self, clutch_context):
        pipeline = NarrationPipeline(rng=SeededRNG(42))
        events = [
            BallAdvanceEvent(ball_handler_name="Curry"),
            ShotResultEvent(
                shooter_name="Curry", made=True, points=3, is_three=True,
            ),
        ]
        output = pipeline.narrate(events, clutch_context)
        assert "!" in output  # should be intense in clutch

    def test_multiple_possessions_vary(self, pipeline, context):
        """Anti-repetition: consecutive possessions should differ."""
        events1 = _harden_ankle_breaker_events()
        events2 = _simple_catch_and_shoot()
        events3 = _fast_break_dunk()

        out1 = pipeline.narrate(events1, context)
        out2 = pipeline.narrate(events2, context)
        out3 = pipeline.narrate(events3, context)

        # All should be non-empty
        assert out1 and out2 and out3
        # All should be different
        assert out1 != out2
        assert out2 != out3

    def test_turnover_event(self, pipeline, context):
        events = [
            BallAdvanceEvent(ball_handler_name="Mitchell"),
            TurnoverEvent(
                player_name="Mitchell",
                is_steal=True,
                stealer_name="Smart",
            ),
        ]
        output = pipeline.narrate(events, context)
        assert len(output) > 0

    def test_block_event(self, pipeline, context):
        events = [
            BallAdvanceEvent(ball_handler_name="Mitchell"),
            DriveEvent(driver_name="Mitchell", defender_name="Williams"),
            BlockEvent(
                blocker_name="Williams",
                shooter_name="Mitchell",
            ),
        ]
        output = pipeline.narrate(events, context)
        assert len(output) > 0

    def test_foul_and_free_throw(self, pipeline, context):
        events = [
            BallAdvanceEvent(ball_handler_name="Harden"),
            DriveEvent(driver_name="Harden"),
            FoulEvent(fouler_name="Smart", victim_name="Harden"),
            FreeThrowEvent(shooter_name="Harden", made=True),
        ]
        output = pipeline.narrate(events, context)
        assert len(output) > 0

    def test_pick_and_roll_sequence(self, pipeline, context):
        events = [
            BallAdvanceEvent(ball_handler_name="Trae"),
            ScreenEvent(
                handler_name="Trae", screener_name="Collins",
                screen_type="ball_screen",
            ),
            DriveEvent(driver_name="Trae", defender_name="Smart"),
            PassEvent(
                passer_name="Trae", receiver_name="Collins",
                is_kick_out=True,
            ),
            ShotResultEvent(
                shooter_name="Collins", made=True, points=2,
                is_dunk=True,
            ),
        ]
        output = pipeline.narrate(events, context)
        assert len(output) > 0

    def test_rebound_event(self, pipeline, context):
        events = [
            ShotResultEvent(shooter_name="Harden", made=False),
            ReboundEvent(
                rebounder_name="Adams", is_offensive=False,
            ),
        ]
        output = pipeline.narrate(events, context)
        assert len(output) > 0
        assert "Adams" in output or "adams" in output.lower()
