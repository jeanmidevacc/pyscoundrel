"""Deck implementation for PyScoundrel."""

import random
from typing import List, Optional, TYPE_CHECKING
from .card import Card, Rank, Suit

if TYPE_CHECKING:
    from ..dungeon import Dungeon


class Deck:
    """
    The Dungeon deck for Scoundrel.

    Manages the draw pile, following Scoundrel setup rules:
    - Remove Jokers, Red Face Cards, and Red Aces
    - Remaining 44 cards: 26 Monsters, 9 Weapons, 9 Health Potions
    """

    def __init__(self, shuffle: bool = True, seed: Optional[int] = None):
        """
        Initialize a new deck (LEGACY: uses playing cards).

        NOTE: This method is deprecated. Use Deck.from_dungeon() instead.
        Only kept for backward compatibility.

        Args:
            shuffle: Whether to shuffle the deck on creation
            seed: Random seed for reproducible shuffling
        """
        self._cards: List[Card] = []
        self._seed = seed
        self._setup_deck()
        if shuffle:
            self.shuffle()

    def _setup_deck(self) -> None:
        """
        Create a standard Scoundrel deck using playing cards (LEGACY).

        NOTE: This creates cards with playing card references (suits, ranks).
        The default game now uses dungeon configurations instead.
        """
        self._cards = []

        for suit in Suit:
            for rank in Rank:
                # Skip red face cards and red aces per game rules
                if suit.is_red and rank.is_face_card:
                    continue

                self._cards.append(Card.from_playing_card(rank=rank, suit=suit))

    @classmethod
    def from_dungeon(cls, dungeon: "Dungeon", shuffle: bool = True, seed: Optional[int] = None) -> "Deck":
        """
        Create a deck from a dungeon configuration.

        Args:
            dungeon: Dungeon card pool configuration
            shuffle: Whether to shuffle the deck
            seed: Random seed for reproducible shuffling

        Returns:
            A new Deck instance built from the dungeon
        """
        deck = cls.__new__(cls)
        deck._cards = []
        deck._seed = seed

        # Build deck from dungeon card definitions
        for card_def in dungeon.card_definitions:
            # Add 'count' copies of each card
            for _ in range(card_def.count):
                card = Card.from_dungeon_card(
                    card_id=card_def.id,
                    name=card_def.name,
                    card_type=card_def.card_type,
                    value=card_def.value
                )
                deck._cards.append(card)

        if shuffle:
            deck.shuffle()

        return deck

    def shuffle(self) -> None:
        """Shuffle the deck."""
        if self._seed is not None:
            random.seed(self._seed)
        random.shuffle(self._cards)

    def draw(self) -> Optional[Card]:
        """
        Draw a card from the top of the deck.

        Returns:
            The drawn card, or None if deck is empty
        """
        if not self._cards:
            return None
        return self._cards.pop(0)

    def draw_multiple(self, count: int) -> List[Card]:
        """
        Draw multiple cards from the deck.

        Args:
            count: Number of cards to draw

        Returns:
            List of drawn cards (may be fewer than requested if deck runs out)
        """
        drawn = []
        for _ in range(count):
            card = self.draw()
            if card is None:
                break
            drawn.append(card)
        return drawn

    def add_to_bottom(self, cards: List[Card]) -> None:
        """
        Add cards to the bottom of the deck (used when avoiding a room).

        Args:
            cards: Cards to add to bottom of deck
        """
        self._cards.extend(cards)

    def peek(self, count: int = 1) -> List[Card]:
        """
        Peek at the top cards without drawing them.

        Args:
            count: Number of cards to peek at

        Returns:
            List of cards at the top of the deck
        """
        return self._cards[:count].copy()

    @property
    def remaining(self) -> int:
        """Get the number of cards remaining in the deck."""
        return len(self._cards)

    @property
    def is_empty(self) -> bool:
        """Check if the deck is empty."""
        return len(self._cards) == 0

    @property
    def cards(self) -> List[Card]:
        """Get a copy of all remaining cards in the deck."""
        return self._cards.copy()

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        return f"Deck(remaining={self.remaining})"
