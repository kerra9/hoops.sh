"""Tests for pairwise relationship model."""

from __future__ import annotations

import pytest

from hoops_sim.models.relationships import Relationship, RelationshipMatrix


class TestRelationship:
    def test_defaults(self):
        r = Relationship()
        assert r.affinity == 0
        assert r.trust == 50
        assert r.rivalry == 0

    def test_clamp(self):
        r = Relationship(affinity=200, trust=-50, rivalry=150)
        r.clamp()
        assert r.affinity == 100
        assert r.trust == 0
        assert r.rivalry == 100

    def test_passing_mod(self):
        positive = Relationship(affinity=50)
        negative = Relationship(affinity=-50)
        assert positive.on_court_passing_mod() > 0
        assert negative.on_court_passing_mod() < 0

    def test_screen_mod(self):
        high_trust = Relationship(trust=100)
        low_trust = Relationship(trust=0)
        assert high_trust.on_court_screen_mod() > low_trust.on_court_screen_mod()

    def test_help_defense_mod(self):
        r = Relationship(trust=100)
        assert r.on_court_help_defense_mod() > 0

    def test_is_positive(self):
        assert Relationship(affinity=10).is_positive()
        assert not Relationship(affinity=-10).is_positive()

    def test_is_strong_bond(self):
        assert Relationship(affinity=60, trust=80).is_strong_bond()
        assert not Relationship(affinity=20, trust=80).is_strong_bond()

    def test_is_toxic(self):
        assert Relationship(affinity=-60).is_toxic()
        assert not Relationship(affinity=-30).is_toxic()


class TestRelationshipMatrix:
    def test_get_creates_default(self):
        matrix = RelationshipMatrix()
        rel = matrix.get(1, 2)
        assert rel.affinity == 0
        assert rel.trust == 50

    def test_symmetric_key(self):
        matrix = RelationshipMatrix()
        matrix.modify_affinity(1, 2, 10)
        rel = matrix.get(2, 1)  # Reversed order
        assert rel.affinity == 10

    def test_modify_affinity(self):
        matrix = RelationshipMatrix()
        matrix.modify_affinity(1, 2, 20)
        assert matrix.get(1, 2).affinity == 20
        matrix.modify_affinity(1, 2, -5)
        assert matrix.get(1, 2).affinity == 15

    def test_modify_trust(self):
        matrix = RelationshipMatrix()
        matrix.modify_trust(1, 2, 10)
        assert matrix.get(1, 2).trust == 60  # 50 default + 10

    def test_all_relationships_for(self):
        matrix = RelationshipMatrix()
        matrix.modify_affinity(1, 2, 10)
        matrix.modify_affinity(1, 3, 20)
        matrix.modify_affinity(2, 3, 5)

        rels = matrix.all_relationships_for(1)
        assert len(rels) == 2
        assert 2 in rels
        assert 3 in rels

    def test_team_chemistry_score(self):
        matrix = RelationshipMatrix()
        # Good team
        matrix.set(1, 2, Relationship(affinity=50, trust=80))
        matrix.set(1, 3, Relationship(affinity=40, trust=70))
        matrix.set(2, 3, Relationship(affinity=30, trust=75))
        score = matrix.team_chemistry_score()
        assert score > 0

    def test_team_chemistry_negative(self):
        matrix = RelationshipMatrix()
        matrix.set(1, 2, Relationship(affinity=-50, trust=20))
        matrix.set(1, 3, Relationship(affinity=-40, trust=10))
        score = matrix.team_chemistry_score()
        assert score < 0

    def test_empty_chemistry(self):
        matrix = RelationshipMatrix()
        assert matrix.team_chemistry_score() == 0.0
