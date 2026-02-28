"""Unit tests for pyscoundrel.models.deck"""

from unittest.mock import MagicMock

import pytest

from pyscoundrel.dungeon.card_pool import CardDefinition
from pyscoundrel.models.card import CardType
from pyscoundrel.models.deck import Deck

pytestmark = pytest.mark.unit


def _make_dungeon(*card_defs):
    """Build a minimal mock Dungeon with the given CardDefinitions."""
    dungeon = MagicMock()
    dungeon.card_definitions = list(card_defs)
    return dungeon


@pytest.fixture
def sample_dungeon():
    return _make_dungeon(
        CardDefinition(id="goblin_01", name="Goblin", card_type=CardType.MONSTER, value=5, count=3),
        CardDefinition(id="sword_01", name="Sword", card_type=CardType.WEAPON, value=8, count=2),
        CardDefinition(
            id="potion_01", name="Potion", card_type=CardType.HEALTH_POTION, value=6, count=2
        ),
    )


class TestDeckInit:
    def test_creates_correct_total_card_count(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        assert len(deck) == 7  # 3 + 2 + 2

    def test_respects_card_definition_count(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        monster_count = sum(1 for c in deck.cards if c.card_type == CardType.MONSTER)
        assert monster_count == 3

    def test_cards_have_correct_types(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        types = {c.card_type for c in deck.cards}
        assert types == {CardType.MONSTER, CardType.WEAPON, CardType.HEALTH_POTION}

    def test_seed_produces_reproducible_order(self, sample_dungeon):
        deck_a = Deck(sample_dungeon, shuffle=True, seed=42)
        deck_b = Deck(sample_dungeon, shuffle=True, seed=42)
        assert [c.card_id for c in deck_a.cards] == [c.card_id for c in deck_b.cards]

    def test_different_seeds_produce_different_orders(self, sample_dungeon):
        deck_a = Deck(sample_dungeon, shuffle=True, seed=1)
        deck_b = Deck(sample_dungeon, shuffle=True, seed=2)
        # With 7 cards it's theoretically possible but extremely unlikely to match
        assert [c.card_id for c in deck_a.cards] != [c.card_id for c in deck_b.cards]


class TestDeckDraw:
    def test_draw_returns_a_card(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        card = deck.draw()
        assert card is not None

    def test_draw_reduces_remaining(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        before = deck.remaining
        deck.draw()
        assert deck.remaining == before - 1

    def test_draw_returns_none_when_empty(self):
        empty_dungeon = _make_dungeon()
        deck = Deck(empty_dungeon, shuffle=False)
        assert deck.draw() is None

    def test_draw_multiple_returns_requested_count(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        cards = deck.draw_multiple(3)
        assert len(cards) == 3

    def test_draw_multiple_returns_fewer_when_deck_runs_short(self):
        small_dungeon = _make_dungeon(
            CardDefinition(
                id="goblin_01", name="Goblin", card_type=CardType.MONSTER, value=5, count=2
            ),
        )
        deck = Deck(small_dungeon, shuffle=False)
        cards = deck.draw_multiple(10)
        assert len(cards) == 2


class TestDeckAddToBottom:
    def test_adds_cards_to_end(self, sample_dungeon, monster_card):
        deck = Deck(sample_dungeon, shuffle=False)
        before = deck.remaining
        deck.add_to_bottom([monster_card])
        assert deck.remaining == before + 1
        assert deck.cards[-1] == monster_card


class TestDeckPeek:
    def test_peek_does_not_remove_cards(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        before = deck.remaining
        deck.peek(2)
        assert deck.remaining == before

    def test_peek_returns_top_cards(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        top = deck.cards[0]
        peeked = deck.peek(1)
        assert peeked[0] == top


class TestDeckProperties:
    def test_is_empty_false_when_has_cards(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        assert deck.is_empty is False

    def test_is_empty_true_when_no_cards(self):
        deck = Deck(_make_dungeon(), shuffle=False)
        assert deck.is_empty is True

    def test_cards_returns_copy(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        copy = deck.cards
        copy.clear()
        assert deck.remaining > 0

    def test_repr_format(self, sample_dungeon):
        deck = Deck(sample_dungeon, shuffle=False)
        assert repr(deck) == f"Deck(remaining={deck.remaining})"
