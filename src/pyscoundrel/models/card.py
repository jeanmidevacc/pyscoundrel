"""Card models and enums for PyScoundrel."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CardType(Enum):
    """Types of cards in Scoundrel."""

    MONSTER = "Monster"
    WEAPON = "Weapon"
    HEALTH_POTION = "Health Potion"


@dataclass(frozen=True)
class Card:
    """A card in Scoundrel, defined by dungeon configuration."""

    card_type: CardType
    value: int
    name: str
    card_id: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get a display name for the card."""
        return self.name

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        if self.card_id:
            return f"Card(id={self.card_id}, name={self.name})"
        return f"Card(name={self.name})"

    @staticmethod
    def from_dungeon_card(card_id: str, name: str, card_type: CardType, value: int) -> "Card":
        """Create a Card from dungeon card definition."""
        return Card(card_type=card_type, value=value, name=name, card_id=card_id)
