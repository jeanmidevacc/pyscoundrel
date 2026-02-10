"""Card models and enums for PyScoundrel."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Suit(Enum):
    """Card suits."""
    CLUBS = "♣"
    SPADES = "♠"
    DIAMONDS = "♦"
    HEARTS = "♥"

    @property
    def is_black(self) -> bool:
        """Check if suit is black."""
        return self in (Suit.CLUBS, Suit.SPADES)

    @property
    def is_red(self) -> bool:
        """Check if suit is red."""
        return self in (Suit.DIAMONDS, Suit.HEARTS)


class Rank(Enum):
    """Card ranks with their numeric values."""
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")

    @property
    def numeric_value(self) -> int:
        """Get the numeric value of the rank."""
        return self.value[0]

    @property
    def display(self) -> str:
        """Get the display string for the rank."""
        return self.value[1]

    @property
    def is_face_card(self) -> bool:
        """Check if rank is a face card."""
        return self in (Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE)


class CardType(Enum):
    """Types of cards in Scoundrel."""
    MONSTER = "Monster"
    WEAPON = "Weapon"
    HEALTH_POTION = "Health Potion"


@dataclass(frozen=True)
class Card:
    """
    A card in Scoundrel.

    Supports both classic playing card format and dungeon-based custom cards.
    """
    # Core properties (always present)
    card_type: CardType
    value: int
    name: str

    # Legacy playing card properties (optional)
    rank: Optional[Rank] = None
    suit: Optional[Suit] = None

    # Dungeon card properties (optional)
    card_id: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get a display name for the card."""
        # Prefer custom name, fall back to playing card format
        if self.rank is not None and self.suit is not None:
            return f"{self.rank.display}{self.suit.value}"
        return self.name

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        if self.card_id:
            return f"Card(id={self.card_id}, name={self.name})"
        elif self.rank and self.suit:
            return f"Card({self.rank.name}, {self.suit.name})"
        else:
            return f"Card(name={self.name})"

    @staticmethod
    def from_playing_card(rank: Rank, suit: Suit) -> "Card":
        """
        Create a Card from playing card components (legacy format).

        Card types are determined by suit:
        - Clubs & Spades: Monsters (damage = rank value)
        - Diamonds: Weapons (damage = rank value)
        - Hearts: Health Potions (heal = rank value)
        """
        # Determine card type from suit
        if suit in (Suit.CLUBS, Suit.SPADES):
            card_type = CardType.MONSTER
        elif suit == Suit.DIAMONDS:
            card_type = CardType.WEAPON
        else:  # Hearts
            card_type = CardType.HEALTH_POTION

        name = f"{rank.display}{suit.value}"

        return Card(
            card_type=card_type,
            value=rank.numeric_value,
            name=name,
            rank=rank,
            suit=suit
        )

    @staticmethod
    def from_dungeon_card(card_id: str, name: str, card_type: CardType, value: int) -> "Card":
        """Create a Card from dungeon card definition."""
        return Card(
            card_type=card_type,
            value=value,
            name=name,
            card_id=card_id
        )

    @staticmethod
    def should_be_removed_in_setup(rank: Rank, suit: Suit) -> bool:
        """
        Check if a playing card should be removed during setup.

        Removed cards: Jokers, Red Face Cards, Red Aces
        """
        if suit.is_red and (rank.is_face_card or rank == Rank.ACE):
            return True
        return False
