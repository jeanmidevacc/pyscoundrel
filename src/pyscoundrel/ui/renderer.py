"""Game renderer using Rich for PyScoundrel."""

from typing import Optional, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .theme import RetroTheme
from ..game.state import GameState, GamePhase
from ..models import Card, Room, CardType


class GameRenderer:
    """Renders the game using Rich library with modern numbered menu."""

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the game renderer.

        Args:
            console: Optional Rich console (creates new one if not provided)
        """
        self.theme = RetroTheme()
        self.console = console or Console(theme=self.theme.get_rich_theme())

    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()

    def show_title(self) -> None:
        """Display the game title screen."""
        self.clear()
        self.console.print()
        title = Panel(
            "[title]SCOUNDREL[/title]\n[muted] A Single Player Rogue-like Card Game by Zach Gage and Kurt Bieg[/muted]",
            box=box.DOUBLE,
            border_style="accent",
            padding=(1, 4),
        )
        self.console.print(title)
        self.console.print()

    def render_game_state(self, state: GameState) -> None:
        """
        Render the complete game state.

        Args:
            state: Current game state
        """
        self.console.print()

        # Status bar
        self._render_status_bar(state)

        # Room display
        if state.current_room:
            self._render_room_panel(state)

            # Choice menu
            if state.phase in (GamePhase.DECIDE_AVOID, GamePhase.FACE_CARDS):
                self._render_choice_menu(state)

    def _render_status_bar(self, state: GameState) -> None:
        """Render status bar with player info."""
        player = state.player
        health_color = self.theme.get_health_color(player.health, player.max_health)
        health_percent = int((player.health / player.max_health) * 100)

        # Create status table
        status = Table.grid(padding=(0, 2))
        status.add_column(justify="left")
        status.add_column(justify="center")
        status.add_column(justify="right")

        # Left: Turn and deck
        left = Text()
        left.append(f"Turn {state.turn_number}", style="accent")

        # Center: Health
        center = Text()
        center.append("❤ ", style=health_color)
        center.append(f"{player.health}/{player.max_health} HP ", style=health_color)
        center.append(f"({health_percent}%)", style="muted")

        # Right: Weapon
        right = Text()
        if player.has_weapon:
            weapon = player.equipped_weapon
            right.append("⚔ ", style="card.weapon")
            right.append(f"{weapon.card.display_name} ", style="card.weapon")
            right.append(f"(DMG: {weapon.damage}", style="info")
            if weapon.is_used:
                right.append(f", Max: {weapon.max_kill_value}", style="muted")
            right.append(")", style="info")
        else:
            right.append("⚔ No Weapon", style="muted")

        status.add_row(left, center, right)

        panel = Panel(status, border_style="border", box=box.ROUNDED)
        self.console.print(panel)

    def _render_room_panel(self, state: GameState) -> None:
        """Render room with cards."""
        room = state.current_room
        player = state.player

        # Build cards table
        table = Table(
            title="[header]Current Room[/header]",
            box=box.ROUNDED,
            border_style="border",
            show_header=True,
            padding=(0, 1),
        )

        table.add_column("Card", justify="center", width=8)
        table.add_column("Type", justify="left", width=12)
        table.add_column("Value", justify="center", width=6)
        table.add_column("If You Face It", justify="left", width=45)
        table.add_column("Status", justify="center", width=10)

        for i, card in enumerate(room.cards):
            is_faced = card in room.cards_faced
            card_type_color = self.theme.get_card_color(card.card_type.name)

            if is_faced:
                # Grayed out
                table.add_row(
                    f"[dim]{card.display_name}[/dim]",
                    f"[dim]{card.card_type.value}[/dim]",
                    f"[dim]{card.value}[/dim]",
                    "[dim]—[/dim]",
                    "[dim]✓ Faced[/dim]",
                )
            else:
                # Available card
                type_symbol = {
                    CardType.MONSTER: "⚠",
                    CardType.WEAPON: "⚔",
                    CardType.HEALTH_POTION: "♥",
                }
                symbol = type_symbol.get(card.card_type, "?")

                # Build effect description
                effect = self._get_card_effect_text(card, player)

                table.add_row(
                    f"[{card_type_color}]{card.display_name}[/{card_type_color}]",
                    f"[{card_type_color}]{symbol} {card.card_type.value}[/{card_type_color}]",
                    f"[{card_type_color}]{card.value}[/{card_type_color}]",
                    effect,
                    "[success]Available[/success]",
                )

        self.console.print(table)
        self.console.print(f"  [muted]Cards faced: {len(room.cards_faced)}/3[/muted]")
        self.console.print()

    def _get_card_effect_text(self, card: Card, player) -> str:
        """Get effect description for a card."""
        if card.card_type == CardType.MONSTER:
            damage_bare = card.value
            text = Text()
            text.append("Fight → ", style="muted")
            text.append(f"Barehanded: {damage_bare} HP", style="damage")

            if player.has_weapon:
                weapon = player.equipped_weapon
                if weapon.can_kill(card):
                    damage_weapon = max(0, card.value - weapon.damage)
                    text.append(" | ", style="muted")
                    text.append(
                        f"With Weapon: {damage_weapon} HP",
                        style="success" if damage_weapon < damage_bare else "damage",
                    )
                else:
                    text.append(" | ", style="muted")
                    text.append(f"Weapon: Can't use", style="muted")

            return text

        elif card.card_type == CardType.WEAPON:
            text = Text()
            text.append(f"Equip weapon ({card.value} DMG)", style="card.weapon")
            if player.has_weapon:
                text.append(" • Replaces current weapon", style="muted")
            return text

        elif card.card_type == CardType.HEALTH_POTION:
            heal = min(card.value, player.max_health - player.health)
            text = Text()
            text.append(f"Heal {heal} HP", style="heal")
            if heal < card.value:
                text.append(f" (max HP reached)", style="muted")
            return text

        return Text("Unknown", style="muted")

    def _render_choice_menu(self, state: GameState) -> None:
        """Render numbered choice menu with all combat options."""
        room = state.current_room
        player = state.player

        # Build choice table
        table = Table(
            title="[choice]▶ Select Your Action[/choice]",
            box=box.ROUNDED,
            border_style="choice",
            show_header=False,
            padding=(0, 2),
        )

        table.add_column("Choice", justify="center", width=8, style="choice.highlight")
        table.add_column("Action", justify="left", width=70)

        choice_num = 1

        # Option to avoid room (only show if available)
        if state.phase == GamePhase.DECIDE_AVOID and state.can_avoid_room:
            table.add_row(
                f"[choice.highlight] {choice_num} [/choice.highlight]",
                "[choice]Avoid this room[/choice] [muted](place cards at bottom of deck)[/muted]",
            )
            choice_num += 1

        # Cards - expand monsters into barehanded + weapon choices
        for i, card in enumerate(room.cards):
            if card not in room.cards_faced:
                card_type_color = self.theme.get_card_color(card.card_type.name)
                type_symbol = {
                    CardType.MONSTER: "⚠",
                    CardType.WEAPON: "⚔",
                    CardType.HEALTH_POTION: "♥",
                }
                symbol = type_symbol.get(card.card_type, "?")

                if card.card_type == CardType.MONSTER:
                    # For monsters, show both combat options
                    damage_bare = card.value

                    # Barehanded option
                    table.add_row(
                        f"[choice.highlight] {choice_num} [/choice.highlight]",
                        f"[{card_type_color}]Face {symbol} {card.display_name} - Barehanded[/{card_type_color}] [damage]({damage_bare} HP)[/damage]",
                    )
                    choice_num += 1

                    # Weapon option (only if available and can be used)
                    if player.has_weapon:
                        weapon = player.equipped_weapon
                        if weapon.can_kill(card):
                            damage_weapon = max(0, card.value - weapon.damage)
                            color = "success" if damage_weapon < damage_bare else "damage"
                            table.add_row(
                                f"[choice.highlight] {choice_num} [/choice.highlight]",
                                f"[{card_type_color}]Face {symbol} {card.display_name} - With Weapon[/{card_type_color}] [{color}]({damage_weapon} HP)[/{color}]",
                            )
                            choice_num += 1

                else:
                    # Non-monsters: single option
                    table.add_row(
                        f"[choice.highlight] {choice_num} [/choice.highlight]",
                        f"[{card_type_color}]Face {symbol} {card.display_name} ({card.card_type.value})[/{card_type_color}]",
                    )
                    choice_num += 1

        # Quit option
        table.add_row(f"[warning] 0 [/warning]", "[warning]Quit Game[/warning]")

        self.console.print(table)
        self.console.print()

    def show_combat_menu(self, monster: Card, can_use_weapon: bool, weapon=None) -> None:
        """Show combat choice menu."""
        monster_color = self.theme.get_card_color(monster.card_type.name)

        # Combat header
        header = Panel(
            f"[{monster_color}]⚠ Combat: {monster.display_name} (Value: {monster.value})[/{monster_color}]",
            border_style="warning",
            box=box.ROUNDED,
        )
        self.console.print(header)

        # Combat options table
        table = Table(
            title="[choice]▶ Choose Combat Method[/choice]",
            box=box.ROUNDED,
            border_style="choice",
            show_header=False,
            padding=(0, 2),
        )

        table.add_column("Choice", justify="center", width=8, style="choice.highlight")
        table.add_column("Method", justify="left", width=25)
        table.add_column("Damage", justify="center", width=15)

        # Barehanded
        damage_bare = monster.value
        table.add_row(
            "[choice.highlight] 1 [/choice.highlight]",
            "[choice]Fight Barehanded[/choice]",
            f"[damage]{damage_bare} HP[/damage]",
        )

        # Weapon
        if weapon and can_use_weapon:
            damage_weapon = max(0, monster.value - weapon.damage)
            color = "success" if damage_weapon < damage_bare else "damage"
            table.add_row(
                "[choice.highlight] 2 [/choice.highlight]",
                f"[choice]Use Weapon ({weapon.card.display_name})[/choice]",
                f"[{color}]{damage_weapon} HP[/{color}]",
            )
        elif weapon:
            table.add_row(
                "[dim]2[/dim]",
                f"[dim]Use Weapon (max kill: {weapon.max_kill_value})[/dim]",
                "[dim]Can't use[/dim]",
            )
        else:
            table.add_row("[dim]2[/dim]", "[dim]No weapon equipped[/dim]", "[dim]—[/dim]")

        # Quit
        table.add_row("[warning] 0 [/warning]", "[warning]Quit Game[/warning]", "")

        self.console.print(table)
        self.console.print()

    def show_action_result(self, message: str, damage: int = 0, heal: int = 0) -> None:
        """Show the result of an action."""
        text = Text()
        text.append("▶ ", style="accent")
        text.append(message)

        if damage > 0:
            text.append(f" [−{damage} HP]", style="damage")

        if heal > 0:
            text.append(f" [+{heal} HP]", style="heal")

        self.console.print(Panel(text, border_style="info", box=box.ROUNDED, expand=False))

    def show_message(self, message: str, style: str = "info") -> None:
        """Show a message to the user."""
        self.console.print(f"[{style}]{message}[/{style}]")

    def show_error(self, message: str) -> None:
        """Show an error message."""
        self.console.print(
            Panel(
                f"[warning]✗ {message}[/warning]",
                border_style="warning",
                box=box.ROUNDED,
                expand=False,
            )
        )

    def show_game_over(self, state: GameState) -> None:
        """Display game over screen."""
        self.console.print()

        if state.victory:
            title = "[success]🎉 VICTORY! 🎉[/success]"
            border = "success"
        else:
            title = "[warning]💀 DEFEATED 💀[/warning]"
            border = "warning"

        health_color = self.theme.get_health_color(state.player.health, state.player.max_health)

        content = Text()
        content.append(f"Final Health: ", style="header")
        content.append(f"{state.player.health}/{state.player.max_health}\n", style=health_color)
        content.append(f"Final Score: ", style="header")
        content.append(f"{state.score}", style="score")

        panel = Panel(content, title=title, border_style=border, box=box.DOUBLE, padding=(1, 4))

        self.console.print(panel)
        self.console.print()

    def render_card_list(self, cards: List[Card], title: str = "Cards") -> None:
        """Render a list of cards."""
        table = Table(title=f"[title]{title}[/title]", box=box.ROUNDED)
        table.add_column("#", justify="right", style="accent")
        table.add_column("Card", justify="center")
        table.add_column("Type", justify="center")
        table.add_column("Value", justify="center")

        for i, card in enumerate(cards, 1):
            card_type_color = self.theme.get_card_color(card.card_type.name)
            table.add_row(
                str(i),
                f"[{card_type_color}]{card.display_name}[/{card_type_color}]",
                f"[{card_type_color}]{card.card_type.value}[/{card_type_color}]",
                str(card.value),
            )

        self.console.print(table)
