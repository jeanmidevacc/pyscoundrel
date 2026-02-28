"""Weapon model for PyScoundrel."""

from dataclasses import dataclass, field
from typing import List, Optional
from .card import Card, CardType


@dataclass
class Weapon:
    """
    An equipped weapon in Scoundrel.

    Weapons have a unique mechanic: once used on a monster, they can only
    be used on monsters of equal or lower value than the last monster killed.
    """

    card: Card
    slain_monsters: List[Card] = field(default_factory=list)

    def __post_init__(self):
        """Validate that the card is actually a weapon."""
        if self.card.card_type != CardType.WEAPON:
            raise ValueError(f"Card {self.card} is not a weapon!")

    @property
    def damage(self) -> int:
        """Get the weapon's damage value."""
        return self.card.value

    @property
    def last_kill_value(self) -> Optional[int]:
        """
        Get the value of the last monster killed with this weapon.

        Returns None if the weapon is unused.
        """
        if not self.slain_monsters:
            return None
        return self.slain_monsters[-1].value

    @property
    def max_kill_value(self) -> Optional[int]:
        """
        Get the maximum monster value this weapon can currently kill.

        After first use, weapons can only kill monsters <= last kill value.
        If unused, returns None (can kill any monster).
        """
        return self.last_kill_value

    @property
    def is_used(self) -> bool:
        """Check if the weapon has been used to kill a monster."""
        return len(self.slain_monsters) > 0

    def can_kill(self, monster: Card) -> bool:
        """
        Check if this weapon can be used against a monster.

        Args:
            monster: The monster card to check

        Returns:
            True if weapon can be used, False otherwise
        """
        if monster.card_type != CardType.MONSTER:
            raise ValueError(f"Card {monster} is not a monster!")

        # Unused weapons can kill any monster
        if not self.is_used:
            return True

        # Used weapons can only kill monsters <= last kill value
        last_kill = self.last_kill_value
        return monster.value <= last_kill

    def attack(self, monster: Card) -> int:
        """
        Use the weapon to attack a monster.

        Args:
            monster: The monster to attack

        Returns:
            Damage taken by the player (monster damage - weapon damage, min 0)

        Raises:
            ValueError: If weapon cannot be used on this monster
        """
        if not self.can_kill(monster):
            raise ValueError(
                f"Weapon {self.card} cannot kill {monster} (last kill: {self.last_kill_value})"
            )

        # Calculate damage: monster value - weapon damage (min 0)
        damage_taken = max(0, monster.value - self.damage)

        # Record the kill
        self.slain_monsters.append(monster)

        return damage_taken

    def __str__(self) -> str:
        if self.is_used:
            return f"{self.card.display_name} (max kill: {self.max_kill_value})"
        return f"{self.card.display_name} (unused)"

    def __repr__(self) -> str:
        return f"Weapon(card={self.card!r}, kills={len(self.slain_monsters)})"
