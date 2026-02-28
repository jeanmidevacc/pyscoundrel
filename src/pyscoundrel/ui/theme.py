"""Modern theme for PyScoundrel UI."""

from rich.theme import Theme
from rich.style import Style


class RetroTheme:
    """
    Modern, clean theme with good contrast and readability.
    """

    # Color palette - Modern, professional colors
    COLORS = {
        "primary_blue": "#3B82F6",  # Bright blue
        "danger_red": "#EF4444",  # Bright red
        "success_green": "#10B981",  # Green
        "warning_amber": "#F59E0B",  # Amber/orange
        "purple": "#8B5CF6",  # Purple
        "cyan": "#06B6D4",  # Cyan
        "slate": "#64748B",  # Neutral slate
        "white": "#F8FAFC",  # Off-white
        "gray": "#94A3B8",  # Light gray
    }

    @classmethod
    def get_rich_theme(cls) -> Theme:
        """Get a Rich theme with modern styling."""
        return Theme(
            {
                # Card types
                "card.monster": Style(color=cls.COLORS["danger_red"], bold=True),
                "card.weapon": Style(color=cls.COLORS["primary_blue"], bold=True),
                "card.potion": Style(color=cls.COLORS["success_green"], bold=True),
                # Game elements
                "health": Style(color=cls.COLORS["success_green"], bold=True),
                "health.low": Style(color=cls.COLORS["danger_red"], bold=True),
                "damage": Style(color=cls.COLORS["danger_red"], bold=True),
                "heal": Style(color=cls.COLORS["success_green"], bold=True),
                # UI elements
                "title": Style(color=cls.COLORS["primary_blue"], bold=True),
                "header": Style(color=cls.COLORS["slate"], bold=True),
                "border": Style(color=cls.COLORS["slate"]),
                "accent": Style(color=cls.COLORS["purple"], bold=True),
                "warning": Style(color=cls.COLORS["danger_red"], bold=True),
                "success": Style(color=cls.COLORS["success_green"], bold=True),
                "info": Style(color=cls.COLORS["cyan"]),
                "choice": Style(color=cls.COLORS["primary_blue"], bold=True),
                "choice.highlight": Style(
                    color=cls.COLORS["warning_amber"], bold=True, reverse=True
                ),
                "muted": Style(color=cls.COLORS["gray"]),
                # Game state
                "phase": Style(color=cls.COLORS["gray"]),
                "score": Style(color=cls.COLORS["warning_amber"], bold=True),
            }
        )

    @classmethod
    def get_card_color(cls, card_type: str) -> str:
        """Get the color for a card type."""
        if card_type == "MONSTER":
            return "card.monster"
        elif card_type == "WEAPON":
            return "card.weapon"
        elif card_type == "HEALTH_POTION":
            return "card.potion"
        return "white"

    @classmethod
    def get_health_color(cls, health: int, max_health: int) -> str:
        """Get health color based on percentage."""
        percentage = health / max_health
        if percentage <= 0.3:
            return "health.low"
        return "health"

    # ASCII Art
    LOGO = r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     ███████╗ ██████╗ ██████╗ ██╗   ██╗███╗   ██╗       ║
║     ██╔════╝██╔════╝██╔═══██╗██║   ██║████╗  ██║       ║
║     ███████╗██║     ██║   ██║██║   ██║██╔██╗ ██║       ║
║     ╚════██║██║     ██║   ██║██║   ██║██║╚██╗██║       ║
║     ███████║╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║       ║
║     ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝       ║
║                                                          ║
║              D R E L                                     ║
║                                                          ║
║           A Roguelike Card Game                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """

    DIVIDER = "─" * 60

    @classmethod
    def get_box_style(cls):
        """Get the box style for panels."""
        from rich import box

        return box.ROUNDED
