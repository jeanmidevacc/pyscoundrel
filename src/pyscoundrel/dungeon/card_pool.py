"""Dungeon card pool loader and manager."""

import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
from ..models import CardType


@dataclass
class CardDefinition:
    """Definition of a card in the dungeon pool."""
    id: str
    name: str
    card_type: CardType
    value: int
    count: int
    description: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict) -> "CardDefinition":
        """Create a CardDefinition from a dictionary."""
        # Map string type to CardType enum
        type_map = {
            "monster": CardType.MONSTER,
            "weapon": CardType.WEAPON,
            "health_potion": CardType.HEALTH_POTION,
        }

        card_type_str = data["type"].lower()
        if card_type_str not in type_map:
            raise ValueError(f"Invalid card type: {data['type']}")

        return CardDefinition(
            id=data["id"],
            name=data["name"],
            card_type=type_map[card_type_str],
            value=data["value"],
            count=data["count"],
            description=data.get("description")
        )


class Dungeon:
    """
    Dungeon card pool loaded from YAML configuration.

    The dungeon represents all possible cards that can appear in the game,
    not the shuffled deck used during play.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize dungeon from YAML configuration.

        Args:
            config_path: Path to dungeon YAML file. If None, uses default.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.version: str = "1.0"
        self.card_definitions: List[CardDefinition] = []
        self._load()

    def _get_default_config_path(self) -> Path:
        """Get path to default dungeon configuration."""
        return Path(__file__).parent / "default_dungeon.yaml"

    def _load(self) -> None:
        """Load dungeon configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Dungeon config not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)

        self.version = data.get("version", "1.0")

        # Load card definitions
        self.card_definitions = []
        for card_data in data.get("cards", []):
            card_def = CardDefinition.from_dict(card_data)
            self.card_definitions.append(card_def)

    def get_total_cards(self) -> int:
        """Get total number of cards in the dungeon pool."""
        return sum(card.count for card in self.card_definitions)

    def get_cards_by_type(self, card_type: CardType) -> List[CardDefinition]:
        """Get all card definitions of a specific type."""
        return [card for card in self.card_definitions if card.card_type == card_type]

    def get_card_by_id(self, card_id: str) -> Optional[CardDefinition]:
        """Get a card definition by its ID."""
        for card in self.card_definitions:
            if card.id == card_id:
                return card
        return None

    def validate(self) -> List[str]:
        """
        Validate the dungeon configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check for duplicate IDs
        ids = [card.id for card in self.card_definitions]
        duplicates = set([id for id in ids if ids.count(id) > 1])
        if duplicates:
            errors.append(f"Duplicate card IDs: {duplicates}")

        # Check that all cards have positive values
        for card in self.card_definitions:
            if card.value <= 0:
                errors.append(f"Card '{card.id}' has non-positive value: {card.value}")
            if card.count <= 0:
                errors.append(f"Card '{card.id}' has non-positive count: {card.count}")

        # Check minimum card counts
        total = self.get_total_cards()
        if total < 20:
            errors.append(f"Dungeon has too few cards: {total} (minimum 20 recommended)")

        return errors

    def __repr__(self) -> str:
        return f"Dungeon(cards={len(self.card_definitions)}, total={self.get_total_cards()})"
