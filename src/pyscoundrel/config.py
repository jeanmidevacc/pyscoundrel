"""Configuration for PyScoundrel."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class GameConfig:
    """Configuration for a Scoundrel game."""

    # Game settings
    random_seed: Optional[int] = None
    starting_health: int = 20
    dungeon_path: Optional[Path] = None  # Path to custom dungeon YAML

    # UI settings
    clear_screen: bool = True
    show_title_screen: bool = True
    headless: bool = False  # Skip all rendering (agent mode only)

    @classmethod
    def default(cls) -> "GameConfig":
        """Get default configuration."""
        return cls()
