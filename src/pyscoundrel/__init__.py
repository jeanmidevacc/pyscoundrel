"""
PyScoundrel - A Python implementation of the Scoundrel card game.

A single-player roguelike card game by Zach Gage and Kurt Bieg.
"""

__version__ = "0.1.2"
__author__ = "PyScoundrel Contributors"

from .dungeon.card_pool import Dungeon
from .game.engine import GameEngine
from .game.state import GameState
from .models.card import Card, CardType
from .models.player import Player
from .models.weapon import Weapon

__all__ = [
    "GameEngine",
    "GameState",
    "Card",
    "CardType",
    "Player",
    "Weapon",
    "Dungeon",
]
