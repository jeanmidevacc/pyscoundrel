"""
Main entry point for PyScoundrel CLI.

Run with: python -m pyscoundrel
"""

import sys
import argparse
import importlib.util
import inspect
from pathlib import Path
from typing import Optional

from .game.engine import GameEngine
from .game.state import GameState, GamePhase
from .game.actions import ActionType, Action
from .ui.renderer import GameRenderer
from .ui.input import InputHandler
from .config import GameConfig
from .models import CardType
from .dungeon import Dungeon
from .agents import Agent
from .logging import GameLogger, serialize_state


class ScoundrelGame:
    """Main game controller."""

    def __init__(self, config: GameConfig, agent: Optional[Agent] = None):
        """
        Initialize the game.

        Args:
            config: Game configuration
            agent: Optional agent for automated gameplay
        """
        self.config = config
        self.agent = agent
        self.renderer = GameRenderer()
        self.input_handler = InputHandler(self.renderer.console)
        self.engine: Optional[GameEngine] = None

        # Initialize logger
        self.logger: Optional[GameLogger] = None
        if config.log_file or config.log_console:
            self.logger = GameLogger(
                log_file=config.log_file,
                log_console=config.log_console
            )

    def setup(self) -> None:
        """Set up the game."""
        # Load dungeon if specified
        dungeon = None
        if self.config.dungeon_path:
            try:
                dungeon = Dungeon(config_path=self.config.dungeon_path)
                errors = dungeon.validate()
                if errors:
                    self.renderer.show_error(f"Dungeon validation errors:")
                    for error in errors:
                        self.renderer.show_error(f"  - {error}")
                    raise ValueError("Invalid dungeon configuration")
            except Exception as e:
                self.renderer.show_error(f"Failed to load dungeon: {e}")
                raise

        # Initialize game engine
        self.engine = GameEngine(seed=self.config.random_seed, dungeon=dungeon)

    def run(self) -> int:
        """
        Run the game.

        Returns:
            Exit code (0 for success)
        """
        try:
            self.setup()

            # Show title screen (not in headless mode)
            if self.config.show_title_screen and not self.config.headless:
                self.renderer.show_title()

            # Start game
            self.engine.start_game()

            # Log game start
            if self.logger:
                self.logger.log(
                    "game_start",
                    {
                        "seed": self.config.random_seed,
                        "starting_health": self.engine.state.player.health,
                        "agent_mode": self.agent is not None
                    },
                    serialize_state(self.engine.state)
                )

            # Main game loop
            while not self.engine.is_game_over:
                should_continue = self._game_loop()
                if not should_continue:
                    # User quit - treat as defeat
                    self.engine.state.mark_quit()
                    break

            # Game over
            self._show_game_over()

            # Close logger
            if self.logger:
                self.logger.close()

            return 0

        except KeyboardInterrupt:
            self.renderer.show_message("\n\nGame interrupted by user.", "warning")
            if self.logger:
                self.logger.close()
            return 1
        except Exception as e:
            self.renderer.show_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            if self.logger:
                self.logger.close()
            return 1

    def _game_loop(self) -> bool:
        """Main game loop iteration.

        Returns:
            True to continue, False to quit
        """
        state = self.engine.state

        # Clear and render current state (skip in headless mode)
        if not self.config.headless:
            if self.config.clear_screen:
                self.renderer.clear()
            self.renderer.render_game_state(state)

        # Handle current phase
        if state.phase == GamePhase.DRAW_ROOM or state.phase == GamePhase.TURN_COMPLETE:
            return self._handle_draw_room()

        elif state.phase == GamePhase.DECIDE_AVOID:
            return self._handle_decide_avoid()

        elif state.phase == GamePhase.FACE_CARDS:
            return self._handle_face_cards()

        return True

    def _handle_draw_room(self) -> bool:
        """Handle drawing a new room.

        Returns:
            True to continue, False to quit
        """
        if not self.config.headless:
            self.renderer.show_message("Drawing new room...", "info")

        result = self.engine.draw_room()

        if result.metadata and result.metadata.get("game_over"):
            return True

        # Log room drawn
        if self.logger and self.engine.state.current_room:
            room = self.engine.state.current_room
            self.logger.log(
                "room_drawn",
                {
                    "cards": [c.name for c in room.cards]
                },
                serialize_state(self.engine.state)
            )

        if not self.config.headless:
            self.renderer.show_action_result(result.message)
        return True

    def _handle_decide_avoid(self) -> bool:
        """Handle decision to avoid room or not.

        Returns:
            True to continue, False to quit
        """
        state = self.engine.state
        room = state.current_room
        player = state.player

        # Build available choices for logging
        available_choices = []
        if state.can_avoid_room:
            available_choices.append({
                "type": "avoid_room",
                "allowed": True
            })

        for card in room.cards:
            if card not in room.cards_faced:
                choice = {
                    "type": "face_card",
                    "card": card.name,
                    "card_type": card.card_type.value,
                    "value": card.value,
                    "methods": []
                }

                if card.card_type == CardType.MONSTER:
                    choice["methods"].append("barehanded")
                    if player.has_weapon and player.equipped_weapon.can_kill(card):
                        choice["methods"].append("weapon")
                else:
                    choice["methods"].append("auto")

                available_choices.append(choice)

        # Agent mode
        if self.agent:
            # Ask agent if it wants to avoid
            should_avoid = self.agent.decide_avoid_room(state)

            if should_avoid and state.can_avoid_room:
                # Log decision
                if self.logger:
                    self.logger.log(
                        "decision",
                        {
                            "phase": "decide_avoid",
                            "available_choices": available_choices,
                            "choice": {"type": "avoid_room"}
                        },
                        serialize_state(state)
                    )

                result = self.engine.avoid_room()
                if not self.config.headless:
                    self.renderer.show_action_result(result.message)
                return True

            # Agent chose to face room - get card choice
            available_cards = [c for c in room.cards if c not in room.cards_faced]
            card_idx, combat_method = self.agent.choose_card(state, available_cards)

            # Log decision
            if self.logger:
                chosen_card = available_cards[card_idx]
                self.logger.log(
                    "decision",
                    {
                        "phase": "decide_avoid",
                        "available_choices": available_choices,
                        "choice": {
                            "type": "face_card",
                            "card": chosen_card.name,
                            "method": combat_method
                        }
                    },
                    serialize_state(state)
                )

            # Convert from available_cards index to room.cards index
            actual_idx = room.cards.index(available_cards[card_idx])
            return self._handle_card_selection(actual_idx, combat_method)

        # Human mode
        # Calculate menu bounds
        menu_start = 1
        avoid_choice = None

        # Option 1: Avoid room (if available)
        if state.can_avoid_room:
            avoid_choice = menu_start
            menu_start += 1

        # Map menu choices to (card_index, combat_method)
        choice_map = {}

        for i, card in enumerate(room.cards):
            if card not in room.cards_faced:
                if card.card_type == CardType.MONSTER:
                    # Barehanded option
                    choice_map[menu_start] = (i, "barehanded")
                    menu_start += 1

                    # Weapon option (only if available and can be used)
                    if player.has_weapon and player.equipped_weapon.can_kill(card):
                        choice_map[menu_start] = (i, "weapon")
                        menu_start += 1
                else:
                    # Non-monster: single choice
                    choice_map[menu_start] = (i, None)
                    menu_start += 1

        max_choice = menu_start - 1

        # Get choice
        choice = self.input_handler.get_menu_choice(0, max_choice)

        if choice == 0:
            # Quit immediately
            return False

        if avoid_choice and choice == avoid_choice:
            # Avoid room
            # Log decision
            if self.logger:
                self.logger.log(
                    "decision",
                    {
                        "phase": "decide_avoid",
                        "available_choices": available_choices,
                        "choice": {"type": "avoid_room"}
                    },
                    serialize_state(state)
                )

            result = self.engine.avoid_room()
            self.renderer.show_action_result(result.message)
            return True

        if choice in choice_map:
            card_idx, combat_method = choice_map[choice]

            # Log decision
            if self.logger:
                chosen_card = room.cards[card_idx]
                self.logger.log(
                    "decision",
                    {
                        "phase": "decide_avoid",
                        "available_choices": available_choices,
                        "choice": {
                            "type": "face_card",
                            "card": chosen_card.name,
                            "method": combat_method if combat_method else "auto"
                        }
                    },
                    serialize_state(state)
                )

            return self._handle_card_selection(card_idx, combat_method)

        return True

    def _handle_face_cards(self) -> bool:
        """Handle facing cards in the room.

        Returns:
            True to continue, False to quit
        """
        state = self.engine.state
        room = state.current_room
        player = state.player

        if not room or room.is_complete:
            return True

        # Agent mode
        if self.agent:
            available_cards = [c for c in room.cards if c not in room.cards_faced]
            card_idx, combat_method = self.agent.choose_card(state, available_cards)

            # Convert from available_cards index to room.cards index
            actual_idx = room.cards.index(available_cards[card_idx])
            return self._handle_card_selection(actual_idx, combat_method)

        # Human mode
        # Map menu choices to (card_index, combat_method)
        choice_map = {}
        menu_num = 1

        for i, card in enumerate(room.cards):
            if card not in room.cards_faced:
                if card.card_type == CardType.MONSTER:
                    # Barehanded option
                    choice_map[menu_num] = (i, "barehanded")
                    menu_num += 1

                    # Weapon option (only if available and can be used)
                    if player.has_weapon and player.equipped_weapon.can_kill(card):
                        choice_map[menu_num] = (i, "weapon")
                        menu_num += 1
                else:
                    # Non-monster: single choice
                    choice_map[menu_num] = (i, None)
                    menu_num += 1

        max_choice = menu_num - 1

        # Get choice
        choice = self.input_handler.get_menu_choice(0, max_choice)

        if choice == 0:
            # Quit immediately
            return False

        if choice in choice_map:
            card_idx, combat_method = choice_map[choice]
            return self._handle_card_selection(card_idx, combat_method)

        return True

    def _handle_card_selection(self, card_num: int, combat_method: str = None) -> bool:
        """Handle selecting and facing a card.

        Args:
            card_num: Card index (0-based)
            combat_method: For monsters: "barehanded" or "weapon", None for non-monsters

        Returns:
            True to continue, False to quit
        """
        room = self.engine.state.current_room

        # Available indices
        available_indices = [
            i for i, card in enumerate(room.cards)
            if card not in room.cards_faced
        ]

        # Check if card is available
        if card_num not in available_indices:
            if not self.config.headless:
                self.renderer.show_error("That card has already been faced!")
            return True

        # Face the card
        result = self.engine.face_card(card_num)

        if not result.success:
            if not self.config.headless:
                self.renderer.show_error(result.message)
            return True

        # Show result
        if not self.config.headless:
            self.renderer.show_action_result(
                result.message,
                damage=result.damage_taken,
                heal=result.health_gained
            )

        # If monster, handle combat with pre-selected method
        if result.metadata and "monster" in result.metadata:
            monster = result.metadata["monster"]
            can_use_weapon = result.metadata.get("can_use_weapon", False)

            # Validate weapon choice
            if combat_method == "weapon" and not can_use_weapon:
                if not self.config.headless:
                    self.renderer.show_error("Cannot use weapon on this monster!")
                return True

            # Execute combat
            if combat_method == "weapon":
                combat_result = self.engine.fight_monster_with_weapon(monster)
            else:
                combat_result = self.engine.fight_monster_barehanded(monster)

            # Log combat
            if self.logger:
                combat_data = {
                    "monster": monster.name,
                    "monster_value": monster.value,
                    "method": combat_method if combat_method else "barehanded"
                }

                if combat_method == "weapon" and self.engine.state.player.has_weapon:
                    weapon = self.engine.state.player.equipped_weapon
                    combat_data["weapon"] = weapon.card.name
                    combat_data["weapon_value"] = weapon.card.value

                if combat_result.damage_taken:
                    combat_data["damage"] = combat_result.damage_taken

                combat_data["health_after"] = self.engine.state.player.health

                self.logger.log(
                    "combat",
                    combat_data,
                    serialize_state(self.engine.state)
                )

            # Show result
            if not self.config.headless:
                self.renderer.show_action_result(
                    combat_result.message,
                    damage=combat_result.damage_taken
                )
        else:
            # Non-monster card faced (weapon or potion)
            if self.logger:
                faced_card = room.cards[card_num]
                card_data = {
                    "card": faced_card.name,
                    "card_type": faced_card.card_type.value,
                    "value": faced_card.value
                }

                if result.health_gained:
                    card_data["health_gained"] = result.health_gained
                    card_data["health_after"] = self.engine.state.player.health

                self.logger.log(
                    "card_faced",
                    card_data,
                    serialize_state(self.engine.state)
                )

        return True

    def _show_game_over(self) -> None:
        """Show game over screen."""
        state = self.engine.state

        # Log game over
        if self.logger:
            self.logger.log(
                "game_over",
                {
                    "victory": state.victory,
                    "score": state.score,
                    "final_health": state.player.health,
                    "reason": "quit" if not state.victory and state.player.health > 0 else ("victory" if state.victory else "death")
                },
                serialize_state(state)
            )

        if self.config.headless:
            # Minimal output for headless mode
            print(f"Game Over - {'Victory' if state.victory else 'Defeat'}")
            print(f"Score: {state.score}")
            print(f"Final Health: {state.player.health}")
        else:
            # Full UI for interactive mode
            if self.config.clear_screen:
                self.renderer.clear()
            self.renderer.show_game_over(state)


def load_agent_from_file(agent_path: Path) -> Agent:
    """
    Load an agent from a Python file.

    The file should contain a class that inherits from Agent
    and is named 'Agent' or have an 'agent' variable/function
    that returns an Agent instance.

    Args:
        agent_path: Path to Python file containing agent

    Returns:
        Instantiated agent

    Raises:
        ValueError: If agent cannot be loaded from file
    """
    try:
        # Load module from file
        spec = importlib.util.spec_from_file_location("agent_module", agent_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load module from {agent_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Try to find Agent class or agent instance
        agent = None

        # Option 1: Look for 'Agent' class by name
        if hasattr(module, 'Agent'):
            agent_class = getattr(module, 'Agent')
            if inspect.isclass(agent_class):
                agent = agent_class()

        # Option 2: Look for 'agent' variable or function
        if agent is None and hasattr(module, 'agent'):
            agent_or_func = getattr(module, 'agent')
            if callable(agent_or_func):
                agent = agent_or_func()
            else:
                agent = agent_or_func

        # Option 3: Search for any class that inherits from Agent
        if agent is None:
            for _, obj in inspect.getmembers(module, inspect.isclass):
                # Skip imported Agent base class itself
                if obj is Agent:
                    continue
                # Check if it's a subclass of Agent
                if issubclass(obj, Agent):
                    agent = obj()
                    break

        # Validate it's an Agent instance
        if agent is None:
            raise ValueError(
                f"No Agent class or agent instance found in {agent_path}. "
                "File should contain either:\n"
                "  - A class named 'Agent' that inherits from pyscoundrel.agents.Agent\n"
                "  - Any class that inherits from pyscoundrel.agents.Agent\n"
                "  - A variable/function named 'agent' that returns an Agent instance"
            )

        if not isinstance(agent, Agent):
            raise ValueError(
                f"Loaded object is not an Agent instance. "
                f"Got {type(agent).__name__} instead. "
                f"Make sure your agent class inherits from pyscoundrel.agents.Agent"
            )

        return agent

    except Exception as e:
        raise ValueError(f"Failed to load agent from {agent_path}: {e}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PyScoundrel - A roguelike card game",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible games"
    )

    parser.add_argument(
        "--no-title",
        action="store_true",
        help="Skip title screen"
    )

    parser.add_argument(
        "--dungeon",
        type=Path,
        help="Path to custom dungeon YAML configuration"
    )

    parser.add_argument(
        "--agent",
        type=Path,
        help="Path to Python file containing agent for automated gameplay"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without UI rendering (requires --agent)"
    )

    parser.add_argument(
        "--log-file",
        nargs="?",
        const="auto",
        type=str,
        help="Log game events to file in JSON format (auto-generates filename if no path provided)"
    )

    parser.add_argument(
        "--log-console",
        action="store_true",
        help="Log game events to console in text format"
    )

    args = parser.parse_args()

    # Validate headless mode requires agent
    if args.headless and not args.agent:
        print("Error: --headless requires --agent to be specified", file=sys.stderr)
        return 1

    # Generate log filename if auto
    log_file = None
    if args.log_file:
        if args.log_file == "auto":
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determine player type
            if args.agent:
                # Extract agent name from filename
                agent_name = args.agent.stem  # e.g., "smart_agent" from "smart_agent.py"
                player_type = agent_name
            else:
                player_type = "human"

            # Create logs directory
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Generate filename: [player_type]_[timestamp].jsonl
            log_file = log_dir / f"{player_type}_{timestamp}.jsonl"
        else:
            log_file = Path(args.log_file)

    # Create configuration
    config = GameConfig(
        random_seed=args.seed,
        show_title_screen=not args.no_title,
        dungeon_path=args.dungeon,
        headless=args.headless,
        log_file=log_file,
        log_console=args.log_console
    )

    # Load agent if specified
    agent = None
    if args.agent:
        try:
            agent = load_agent_from_file(args.agent)
        except ValueError as e:
            print(f"Error loading agent: {e}", file=sys.stderr)
            return 1

    # Run game
    game = ScoundrelGame(config, agent=agent)
    return game.run()


if __name__ == "__main__":
    sys.exit(main())
