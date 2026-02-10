"""
Example script demonstrating programmatic usage of PyScoundrel.

This shows how to use the game engine and models without the CLI interface.
"""

from pyscoundrel.game.engine import GameEngine
from pyscoundrel.logging.logger import GameLogger
from pyscoundrel.config import GameConfig
from pathlib import Path


def simple_game_example():
    """Run a simple automated game."""
    print("=== PyScoundrel Programmatic Example ===\n")

    # Create configuration
    config = GameConfig(
        enable_logging=True,
        log_version="1.0",
        log_file=Path("example_game.log"),
        random_seed=42  # For reproducible results
    )

    # Initialize logger
    logger = GameLogger(
        enabled=config.enable_logging,
        version=config.log_version,
        output_file=config.log_file
    )

    # Initialize game engine
    engine = GameEngine(seed=config.random_seed)

    print(f"Starting game with seed: {config.random_seed}")
    print(f"Logging to: {config.log_file}\n")

    # Log game start
    logger.log_game_start(seed=config.random_seed)

    # Start game
    result = engine.start_game()
    print(f"✓ {result.message}\n")

    turn = 0
    max_turns = 5  # Limit for example

    # Game loop
    while not engine.is_game_over and turn < max_turns:
        turn += 1
        print(f"--- Turn {turn} ---")

        # Draw room
        result = engine.draw_room()
        if result.metadata and result.metadata.get("game_over"):
            break

        print(f"Room: {engine.state.current_room}")
        logger.log_state(engine.state)

        # Simple strategy: always face first available card
        room = engine.state.current_room
        for _ in range(3):  # Face 3 cards
            if room.is_complete:
                break

            # Find first available card
            available_idx = None
            for i, card in enumerate(room.cards):
                if card not in room.cards_faced:
                    available_idx = i
                    break

            if available_idx is None:
                break

            # Face the card
            result = engine.face_card(available_idx)
            card = room.cards[available_idx]

            print(f"  Faced: {card} ({card.card_type.value})")

            # Handle monster
            if result.metadata and "monster" in result.metadata:
                monster = result.metadata["monster"]
                can_use_weapon = result.metadata.get("can_use_weapon", False)

                if can_use_weapon:
                    result = engine.fight_monster_with_weapon(monster)
                    print(f"    → Used weapon! Damage taken: {result.damage_taken}")
                else:
                    result = engine.fight_monster_barehanded(monster)
                    print(f"    → Fought barehanded! Damage taken: {result.damage_taken}")

                if result.is_fatal:
                    print("    → Player died!")
                    break
            elif result.damage_taken > 0:
                print(f"    → Damage taken: {result.damage_taken}")
            elif result.health_gained > 0:
                print(f"    → Health gained: {result.health_gained}")

        # Show player status
        player = engine.state.player
        print(f"  HP: {player.health}/{player.max_health}")
        if player.has_weapon:
            weapon = player.equipped_weapon
            print(f"  Weapon: {weapon}")
        print()

    # Game over
    print("=== Game Over ===")
    print(f"Victory: {engine.state.victory}")
    print(f"Final Health: {engine.state.player.health}/{engine.state.player.max_health}")
    print(f"Score: {engine.score}")
    print(f"Turns Played: {turn}")

    # Log game over
    logger.log_game_over(
        victory=engine.state.victory,
        score=engine.score
    )

    logger.close()

    print(f"\nLog saved to: {config.log_file}")
    print("\nRun the full CLI version with: python -m pyscoundrel")


if __name__ == "__main__":
    simple_game_example()
