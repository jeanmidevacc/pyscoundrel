"""Room model for PyScoundrel."""

from dataclasses import dataclass, field
from typing import List, Optional

from .card import Card


@dataclass
class Room:
    """
    A room in the dungeon containing 4 cards.

    Players must face 3 of the 4 cards, leaving 1 for the next room.
    """

    cards: List[Card] = field(default_factory=list)
    cards_faced: List[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        """
        Add a card to the room.

        Args:
            card: Card to add
        """
        if len(self.cards) >= 4:
            raise ValueError("Room already has 4 cards!")
        self.cards.append(card)

    def face_card(self, index: int) -> Card:
        """
        Face a card from the room by index.

        Args:
            index: Index of card to face (0-3)

        Returns:
            The faced card

        Raises:
            IndexError: If index is invalid
            ValueError: If trying to face more than 3 cards or card already faced
        """
        if len(self.cards_faced) >= 3:
            raise ValueError("Cannot face more than 3 cards per room!")

        if index < 0 or index >= len(self.cards):
            raise IndexError(f"Invalid card index: {index}")

        card = self.cards[index]

        # Check if this card has already been faced
        if card in self.cards_faced:
            raise ValueError(f"Card at index {index} has already been faced!")

        self.cards_faced.append(card)
        return card

    def get_remaining_card(self) -> Optional[Card]:
        """
        Get the one remaining card that wasn't faced.

        Returns:
            The remaining card, or None if not exactly 1 card remains
        """
        if len(self.cards_faced) != 3:
            return None

        for card in self.cards:
            if card not in self.cards_faced:
                return card
        return None

    @property
    def is_full(self) -> bool:
        """Check if room has 4 cards."""
        return len(self.cards) == 4

    @property
    def is_complete(self) -> bool:
        """Check if 3 cards have been faced."""
        return len(self.cards_faced) == 3

    @property
    def available_cards(self) -> List[Card]:
        """Get list of cards that haven't been faced yet."""
        return [c for c in self.cards if c not in self.cards_faced]

    @property
    def num_cards_remaining(self) -> int:
        """Get number of cards not yet faced."""
        return len(self.cards) - len(self.cards_faced)

    def __str__(self) -> str:
        card_strs = []
        for i, card in enumerate(self.cards):
            if card in self.cards_faced:
                card_strs.append(f"[{card.display_name}]")
            else:
                card_strs.append(card.display_name)
        return f"Room: {' '.join(card_strs)}"

    def __repr__(self) -> str:
        return f"Room(cards={len(self.cards)}, faced={len(self.cards_faced)})"
