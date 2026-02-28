"""Unit tests for pyscoundrel.models.card"""

import pytest
from dataclasses import FrozenInstanceError

from pyscoundrel.models.card import Card, CardType

pytestmark = pytest.mark.unit


class TestCardFromDungeonCard:
    def test_creates_card_with_correct_fields(self):
        card = Card.from_dungeon_card(
            card_id="goblin_01",
            name="Goblin",
            card_type=CardType.MONSTER,
            value=5,
        )
        assert card.card_id == "goblin_01"
        assert card.name == "Goblin"
        assert card.card_type == CardType.MONSTER
        assert card.value == 5

    def test_weapon_card(self):
        card = Card.from_dungeon_card("sword_01", "Iron Sword", CardType.WEAPON, 8)
        assert card.card_type == CardType.WEAPON
        assert card.value == 8

    def test_health_potion_card(self):
        card = Card.from_dungeon_card("potion_01", "Healing Herb", CardType.HEALTH_POTION, 6)
        assert card.card_type == CardType.HEALTH_POTION
        assert card.value == 6


class TestCardDisplayName:
    def test_display_name_returns_name(self):
        card = Card.from_dungeon_card("orc_01", "Big Orc", CardType.MONSTER, 12)
        assert card.display_name == "Big Orc"

    def test_str_equals_display_name(self):
        card = Card.from_dungeon_card("sword_01", "Rusty Sword", CardType.WEAPON, 4)
        assert str(card) == card.display_name


class TestCardRepr:
    def test_repr_with_card_id(self):
        card = Card.from_dungeon_card("sword_01", "Rusty Sword", CardType.WEAPON, 6)
        assert repr(card) == "Card(id=sword_01, name=Rusty Sword)"

    def test_repr_without_card_id(self):
        card = Card(card_type=CardType.MONSTER, value=5, name="Unnamed Monster")
        assert repr(card) == "Card(name=Unnamed Monster)"


class TestCardFrozen:
    def test_card_is_immutable(self):
        card = Card.from_dungeon_card("goblin_01", "Goblin", CardType.MONSTER, 3)
        with pytest.raises(FrozenInstanceError):
            card.value = 99  # type: ignore


class TestCardType:
    def test_all_types_exist(self):
        assert CardType.MONSTER.value == "Monster"
        assert CardType.WEAPON.value == "Weapon"
        assert CardType.HEALTH_POTION.value == "Health Potion"
