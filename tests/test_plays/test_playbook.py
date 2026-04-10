"""Tests for the playbook system."""

from hoops_sim.plays.playbook import (
    DEFAULT_PLAYBOOK,
    PICK_AND_ROLL,
    ISOLATION,
    FAST_BREAK,
    PlayType,
    select_play,
)


class TestPlayDefinitions:
    def test_all_plays_have_roles(self):
        for play in DEFAULT_PLAYBOOK:
            assert len(play.roles) == 5, f"{play.name} needs 5 roles"

    def test_all_plays_have_actions(self):
        for play in DEFAULT_PLAYBOOK:
            assert len(play.actions) > 0, f"{play.name} has no actions"

    def test_play_types_unique(self):
        types = [p.play_type for p in DEFAULT_PLAYBOOK]
        assert len(types) == len(set(types))


class TestSelectPlay:
    def test_transition_prefers_fast_break(self):
        counts = {"Fast Break": 0, "other": 0}
        for i in range(100):
            play = select_play(DEFAULT_PLAYBOOK, is_transition=True, rng_value=i / 100)
            if play.play_type == PlayType.FAST_BREAK:
                counts["Fast Break"] += 1
            else:
                counts["other"] += 1
        assert counts["Fast Break"] > 20  # Should be selected frequently

    def test_clutch_prefers_high_clutch_fit(self):
        counts = {"high_clutch": 0, "other": 0}
        for i in range(100):
            play = select_play(
                DEFAULT_PLAYBOOK, is_clutch=True, rng_value=i / 100,
            )
            # Isolation (0.9) and ATO (0.95) are high-clutch plays
            if play.clutch_fit >= 0.8:
                counts["high_clutch"] += 1
            else:
                counts["other"] += 1
        assert counts["high_clutch"] > 15

    def test_empty_playbook_returns_default(self):
        play = select_play([], rng_value=0.5)
        assert play.name == "Pick and Roll"
