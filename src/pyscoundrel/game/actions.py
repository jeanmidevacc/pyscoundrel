"""Player actions in PyScoundrel."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(Enum):
    """Types of actions a player can take."""

    AVOID_ROOM = "avoid_room"
    FACE_CARD = "face_card"
    FIGHT_BAREHANDED = "fight_barehanded"
    FIGHT_WITH_WEAPON = "fight_with_weapon"
    EQUIP_WEAPON = "equip_weapon"
    USE_POTION = "use_potion"
    START_TURN = "start_turn"
    END_TURN = "end_turn"


@dataclass
class Action:
    """
    Represents a player action.

    Args:
        action_type: The type of action
        card_index: Optional index of card in room (for face_card actions)
        metadata: Optional additional data about the action
    """

    action_type: ActionType
    card_index: Optional[int] = None
    metadata: Optional[dict] = None

    def __str__(self) -> str:
        if self.card_index is not None:
            return f"{self.action_type.value}(card={self.card_index})"
        return self.action_type.value

    def __repr__(self) -> str:
        return f"Action({self.action_type.value}, card_index={self.card_index})"


@dataclass
class ActionResult:
    """
    Result of executing an action.

    Args:
        success: Whether the action succeeded
        message: Description of what happened
        damage_taken: Damage taken by the player (if any)
        health_gained: Health gained by the player (if any)
        metadata: Additional result data
    """

    success: bool
    message: str
    damage_taken: int = 0
    health_gained: int = 0
    metadata: Optional[dict] = None

    @property
    def is_fatal(self) -> bool:
        """Check if this action resulted in player death."""
        return self.metadata and self.metadata.get("player_died", False)

    def __str__(self) -> str:
        parts = [self.message]
        if self.damage_taken > 0:
            parts.append(f"(-{self.damage_taken} HP)")
        if self.health_gained > 0:
            parts.append(f"(+{self.health_gained} HP)")
        return " ".join(parts)
