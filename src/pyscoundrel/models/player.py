"""Player model for PyScoundrel."""

from dataclasses import dataclass
from typing import Optional

from .weapon import Weapon


@dataclass
class Player:
    """
    Player state in Scoundrel.

    Tracks health and equipped weapon.
    """

    health: int = 20
    max_health: int = 20
    equipped_weapon: Optional[Weapon] = None
    potions_used_this_turn: int = 0

    def take_damage(self, damage: int) -> None:
        """
        Take damage, reducing health.

        Args:
            damage: Amount of damage to take
        """
        self.health = max(0, self.health - damage)

    def heal(self, amount: int) -> int:
        """
        Heal the player.

        Args:
            amount: Amount to heal

        Returns:
            Actual amount healed (capped at max_health)
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health

    def equip_weapon(self, weapon: Weapon) -> Optional[Weapon]:
        """
        Equip a new weapon, replacing the current one.

        Args:
            weapon: The weapon to equip

        Returns:
            The previously equipped weapon, or None
        """
        old_weapon = self.equipped_weapon
        self.equipped_weapon = weapon
        return old_weapon

    def reset_turn_state(self) -> None:
        """Reset per-turn state (e.g., potion usage counter)."""
        self.potions_used_this_turn = 0

    @property
    def is_alive(self) -> bool:
        """Check if the player is still alive."""
        return self.health > 0

    @property
    def is_dead(self) -> bool:
        """Check if the player is dead."""
        return self.health <= 0

    @property
    def has_weapon(self) -> bool:
        """Check if the player has a weapon equipped."""
        return self.equipped_weapon is not None

    def __str__(self) -> str:
        weapon_str = str(self.equipped_weapon) if self.has_weapon else "None"
        return f"HP: {self.health}/{self.max_health} | Weapon: {weapon_str}"

    def __repr__(self) -> str:
        return f"Player(health={self.health}, weapon={self.equipped_weapon!r})"
