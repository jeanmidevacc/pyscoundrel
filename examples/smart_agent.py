"""
Smart agent for PyScoundrel.

This agent makes more strategic decisions:
- Avoids rooms when health is low
- Prioritizes potions when injured
- Uses weapons strategically
- Chooses lowest-damage monsters when possible

Usage:
    python -m pyscoundrel --agent smart_agent.py --seed 42
"""

from pyscoundrel.agents import Agent as BaseAgent
from pyscoundrel.game.state import GameState
from pyscoundrel.models import Card, CardType


class Agent(BaseAgent):
    """
    A smarter agent that makes strategic decisions.
    """

    def __init__(self):
        self.health_threshold = 8  # Avoid rooms if health below this

    def decide_avoid_room(self, state: GameState) -> bool:
        """
        Avoid room if health is critically low and we can avoid.

        Args:
            state: Current game state

        Returns:
            True if health is below threshold, False otherwise
        """
        return state.player.health <= self.health_threshold

    def choose_card(self, state: GameState, available_cards: list[Card]) -> tuple[int, str]:
        """
        Choose card strategically based on game state.

        Priority:
        1. Potions if health < 15
        2. Weapons if we don't have one
        3. Monsters we can kill with weapon
        4. Lowest damage monster

        Args:
            state: Current game state
            available_cards: List of cards not yet faced in current room

        Returns:
            Tuple of (card_index, method)
        """
        player = state.player

        # Priority 1: Grab potions if injured
        if player.health < 15:
            for i, card in enumerate(available_cards):
                if card.card_type == CardType.HEALTH_POTION:
                    return (i, "auto")

        # Priority 2: Grab weapons if we don't have one
        if not player.has_weapon:
            for i, card in enumerate(available_cards):
                if card.card_type == CardType.WEAPON:
                    return (i, "auto")

        # Priority 3: Fight monsters we can kill with weapon
        if player.has_weapon:
            weapon = player.equipped_weapon
            for i, card in enumerate(available_cards):
                if card.card_type == CardType.MONSTER and weapon.can_kill(card):
                    return (i, "weapon")

        # Priority 4: Choose lowest damage option
        # Find lowest damage monster or any non-monster
        best_idx = 0
        best_damage = float("inf")

        for i, card in enumerate(available_cards):
            if card.card_type == CardType.MONSTER:
                # Calculate damage if we fight barehanded
                damage = card.value
                if damage < best_damage:
                    best_damage = damage
                    best_idx = i
            else:
                # Non-monsters are always good (weapons/potions)
                return (i, "auto")

        # Fight the lowest damage monster barehanded
        return (best_idx, "barehanded")
