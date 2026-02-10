"""Base agent class for PyScoundrel."""

from abc import ABC, abstractmethod
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from pyscoundrel.game.state import GameState
    from pyscoundrel.models.card import Card


class Agent(ABC):
    """
    Abstract base class for PyScoundrel agents.

    Custom agents should inherit from this class and implement
    the decision-making methods.
    """

    @abstractmethod
    def decide_avoid_room(self, state: "GameState") -> bool:
        """
        Decide whether to avoid the current room.

        Args:
            state: Current game state

        Returns:
            True to avoid the room, False to face it
        """
        pass

    @abstractmethod
    def choose_card(
        self,
        state: "GameState",
        available_cards: list["Card"]
    ) -> Tuple[int, str]:
        """
        Choose which card to face and how to handle it.

        Args:
            state: Current game state
            available_cards: List of cards not yet faced in current room

        Returns:
            Tuple of (card_index, method) where:
            - card_index: Index in available_cards list (0-based)
            - method: One of "barehanded", "weapon", or "auto" for non-monsters
        """
        pass
