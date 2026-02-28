"""Shared fixtures for the entire test suite."""

import pytest
from pyscoundrel.models.card import Card, CardType
from pyscoundrel.models.weapon import Weapon
from pyscoundrel.models.player import Player


@pytest.fixture
def monster_card():
    return Card.from_dungeon_card("goblin_01", "Goblin", CardType.MONSTER, 5)


@pytest.fixture
def strong_monster():
    return Card.from_dungeon_card("troll_01", "Troll", CardType.MONSTER, 12)


@pytest.fixture
def weak_monster():
    return Card.from_dungeon_card("rat_01", "Rat", CardType.MONSTER, 2)


@pytest.fixture
def weapon_card():
    return Card.from_dungeon_card("sword_01", "Iron Sword", CardType.WEAPON, 8)


@pytest.fixture
def potion_card():
    return Card.from_dungeon_card("potion_01", "Health Potion", CardType.HEALTH_POTION, 6)


@pytest.fixture
def weapon(weapon_card):
    return Weapon(card=weapon_card)


@pytest.fixture
def player():
    return Player()
