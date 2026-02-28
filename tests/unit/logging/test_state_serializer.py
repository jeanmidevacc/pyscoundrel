"""Unit tests for pyscoundrel.logging.state_serializer"""

import pytest
from unittest.mock import MagicMock, PropertyMock
from pyscoundrel.logging.state_serializer import serialize_card, serialize_state
from pyscoundrel.models.card import Card, CardType
from pyscoundrel.models.weapon import Weapon
from pyscoundrel.models.player import Player
from pyscoundrel.models.room import Room

pytestmark = pytest.mark.unit


def _make_card(name, card_type=CardType.MONSTER, value=5):
    return Card.from_dungeon_card(f"{name}_01", name, card_type, value)


def _make_state(player=None, deck_cards=None, discard_pile=None, current_room=None):
    state = MagicMock()
    state.player = player or Player()
    state.deck._cards = deck_cards or []
    state.discard_pile = discard_pile or []
    state.current_room = current_room
    return state


class TestSerializeCard:
    def test_returns_card_name(self):
        card = _make_card("Goblin")
        assert serialize_card(card) == "Goblin"

    def test_returns_weapon_name(self):
        card = _make_card("Iron Sword", CardType.WEAPON, 8)
        assert serialize_card(card) == "Iron Sword"

    def test_returns_potion_name(self):
        card = _make_card("Health Potion", CardType.HEALTH_POTION, 6)
        assert serialize_card(card) == "Health Potion"


class TestSerializeStatePlayer:
    def test_player_health_included(self):
        player = Player()
        player.health = 15
        state = _make_state(player=player)
        result = serialize_state(state)
        assert result["player"]["health"] == 15

    def test_player_max_health_is_20(self):
        state = _make_state()
        result = serialize_state(state)
        assert result["player"]["max_health"] == 20

    def test_player_weapon_is_none_when_unarmed(self):
        state = _make_state()
        result = serialize_state(state)
        assert result["player"]["weapon"] is None

    def test_player_weapon_included_when_equipped(self):
        player = Player()
        sword_card = _make_card("Sword", CardType.WEAPON, 8)
        player.equip_weapon(Weapon(card=sword_card))
        state = _make_state(player=player)
        result = serialize_state(state)
        weapon = result["player"]["weapon"]
        assert weapon is not None
        assert weapon["card"] == "Sword"
        assert weapon["value"] == 8

    def test_weapon_kills_list_is_empty_when_unused(self):
        player = Player()
        sword_card = _make_card("Sword", CardType.WEAPON, 8)
        player.equip_weapon(Weapon(card=sword_card))
        state = _make_state(player=player)
        result = serialize_state(state)
        assert result["player"]["weapon"]["kills"] == []

    def test_weapon_kills_list_contains_slain_monster_values(self):
        player = Player()
        sword_card = _make_card("Sword", CardType.WEAPON, 8)
        player.equip_weapon(Weapon(card=sword_card))
        rat = _make_card("Rat", CardType.MONSTER, 2)
        player.equipped_weapon.attack(rat)
        state = _make_state(player=player)
        result = serialize_state(state)
        assert result["player"]["weapon"]["kills"] == [2]


class TestSerializeStateDungeon:
    def test_dungeon_count_matches_deck_size(self):
        goblin = _make_card("Goblin")
        sword = _make_card("Sword", CardType.WEAPON, 8)
        state = _make_state(deck_cards=[goblin, sword])
        result = serialize_state(state)
        assert result["dungeon"]["count"] == 2

    def test_dungeon_cards_are_names(self):
        goblin = _make_card("Goblin")
        state = _make_state(deck_cards=[goblin])
        result = serialize_state(state)
        assert result["dungeon"]["cards"] == ["Goblin"]

    def test_dungeon_empty_deck(self):
        state = _make_state(deck_cards=[])
        result = serialize_state(state)
        assert result["dungeon"]["count"] == 0
        assert result["dungeon"]["cards"] == []


class TestSerializeStateDiscard:
    def test_discard_count_matches_pile_size(self):
        goblin = _make_card("Goblin")
        state = _make_state(discard_pile=[goblin])
        result = serialize_state(state)
        assert result["discard"]["count"] == 1

    def test_discard_cards_are_names(self):
        goblin = _make_card("Goblin")
        state = _make_state(discard_pile=[goblin])
        result = serialize_state(state)
        assert result["discard"]["cards"] == ["Goblin"]

    def test_empty_discard(self):
        state = _make_state()
        result = serialize_state(state)
        assert result["discard"]["count"] == 0


class TestSerializeStateRoom:
    def test_room_is_none_when_no_current_room(self):
        state = _make_state(current_room=None)
        result = serialize_state(state)
        assert result["room"] is None

    def test_room_cards_are_names(self):
        room = Room()
        goblin = _make_card("Goblin")
        room.add_card(goblin)
        state = _make_state(current_room=room)
        result = serialize_state(state)
        assert "Goblin" in result["room"]["cards"]

    def test_room_faced_cards_listed(self):
        room = Room()
        goblin = _make_card("Goblin")
        room.add_card(goblin)
        room.cards_faced.append(goblin)
        state = _make_state(current_room=room)
        result = serialize_state(state)
        assert "Goblin" in result["room"]["faced"]

    def test_room_remaining_excludes_faced(self):
        room = Room()
        goblin = _make_card("Goblin")
        sword = _make_card("Sword", CardType.WEAPON, 8)
        room.add_card(goblin)
        room.add_card(sword)
        room.cards_faced.append(goblin)
        state = _make_state(current_room=room)
        result = serialize_state(state)
        assert result["room"]["remaining"] == ["Sword"]
