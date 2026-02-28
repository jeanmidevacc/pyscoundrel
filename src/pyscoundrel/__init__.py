"""
PyScoundrel - A Python implementation of the Scoundrel card game.

A single-player roguelike card game by Zach Gage and Kurt Bieg.
"""

__version__ = "0.1.0"
__author__ = "PyScoundrel Contributors"

from .game.engine import GameEngine
from .game.state import GameState
from .models.card import Card, CardType

__all__ = ["GameEngine", "GameState", "Card", "CardType"]
