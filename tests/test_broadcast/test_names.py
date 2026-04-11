"""Tests for the diverse name generator."""

import random

from hoops_sim.data.names import (
    FIRST_NAMES,
    LAST_NAMES,
    generate_name,
    PLAY_STYLES,
    SIGNATURE_MOVES,
    CELEBRATIONS,
)


class TestNameGenerator:
    def test_pool_sizes(self):
        assert len(FIRST_NAMES) >= 150
        assert len(LAST_NAMES) >= 150

    def test_unique_generation(self):
        rng = random.Random(42)
        used = set()
        names = []
        for _ in range(50):
            first, last = generate_name(rng, used)
            full = f"{first} {last}"
            names.append(full)
            assert full in used

        # All names should be unique
        assert len(set(names)) == len(names)

    def test_no_real_nba_players(self):
        rng = random.Random(42)
        used = set()
        for _ in range(200):
            first, last = generate_name(rng, used)
            full = f"{first} {last}"
            # Should not be a real NBA star
            assert full != "Stephen Curry"
            assert full != "LeBron James"
            assert full != "Kevin Durant"

    def test_play_styles_coverage(self):
        assert "scoring_guard" in PLAY_STYLES
        assert "rim_protector" in PLAY_STYLES
        for archetype, styles in PLAY_STYLES.items():
            assert len(styles) >= 2

    def test_signature_moves_by_position(self):
        assert "guard" in SIGNATURE_MOVES
        assert "wing" in SIGNATURE_MOVES
        assert "big" in SIGNATURE_MOVES

    def test_celebrations_list(self):
        assert len(CELEBRATIONS) >= 10
