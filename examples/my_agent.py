"""
Example agent for PyScoundrel.

This is a simple agent that demonstrates how to create
an automated player for the game.

Usage:
    python -m pyscoundrel --agent my_agent.py --seed 42
"""

from pyscoundrel.agents import Agent as BaseAgent
from pyscoundrel.game.state import GameState
from pyscoundrel.models import Card, CardType


class Agent(BaseAgent):
    """
    Simple example agent that always chooses the first available card.
    """

    def decide_avoid_room(self, state: GameState) -> bool:
        """
        Decide whether to avoid the current room.

        This simple agent never avoids rooms.

        Args:
            state: Current game state

        Returns:
            False (never avoid)
        """
        return False

    def choose_card(
        self,
        state: GameState,
        available_cards: list[Card]
    ) -> tuple[int, str]:
        """
        Choose which card to face and how to handle it.

        This simple agent always chooses the first available card
        and uses a weapon if possible.

        Args:
            state: Current game state
            available_cards: List of cards not yet faced in current room

        Returns:
            Tuple of (card_index, method)
        """
        # Always choose first card
        card = available_cards[0]

        # For monsters, decide combat method
        if card.card_type == CardType.MONSTER:
            # Try to use weapon if we have one and it can kill this monster
            if state.player.has_weapon and state.player.equipped_weapon.can_kill(card):
                return (0, "weapon")
            # Otherwise fight barehanded
            return (0, "barehanded")

        # Non-monsters (weapons, potions) use "auto"
        return (0, "auto")
