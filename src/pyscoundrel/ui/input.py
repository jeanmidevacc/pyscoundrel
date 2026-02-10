"""Input handling for PyScoundrel."""

from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt


class InputHandler:
    """Handles user input with Rich prompts."""

    def __init__(self, console: Console):
        """
        Initialize the input handler.

        Args:
            console: Rich console for prompts
        """
        self.console = console

    def get_menu_choice(self, min_choice: int, max_choice: int) -> int:
        """
        Get a numbered menu choice from the user.

        Args:
            min_choice: Minimum valid choice (usually 0 for quit)
            max_choice: Maximum valid choice

        Returns:
            The user's choice as integer (0 = quit)
        """
        while True:
            try:
                choice = IntPrompt.ask(
                    "[choice]Enter choice[/choice]",
                    console=self.console
                )

                if min_choice <= choice <= max_choice:
                    return choice
                else:
                    self.console.print(f"[warning]Please enter a number between {min_choice} and {max_choice}[/warning]")

            except (ValueError, KeyboardInterrupt):
                self.console.print("[warning]Please enter a valid number[/warning]")

    def confirm(self, prompt: str, default: bool = False) -> bool:
        """
        Get yes/no confirmation from user.

        Args:
            prompt: Confirmation prompt
            default: Default value

        Returns:
            True if confirmed, False otherwise
        """
        return Confirm.ask(prompt, default=default, console=self.console)

    def press_any_key(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user to press Enter."""
        Prompt.ask(f"[dim]{message}[/dim]", default="", show_default=False, console=self.console)
