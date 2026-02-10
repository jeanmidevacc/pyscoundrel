# Dungeon Configuration Guide

PyScoundrel now supports configurable card pools via YAML files, allowing you to create custom dungeons with unique cards instead of using standard playing cards.

## Quick Start

### Using Default Dungeon

The game includes a default dungeon configuration that matches the classic Scoundrel experience:

```python
from pyscoundrel.dungeon import Dungeon
from pyscoundrel.game.engine import GameEngine

# Load default dungeon
dungeon = Dungeon()

# Create game engine with dungeon
engine = GameEngine(dungeon=dungeon, seed=42)
engine.start_game()
```

### Using Custom Dungeon

Create your own YAML configuration:

```bash
python -m pyscoundrel --dungeon my_custom_dungeon.yaml
```

## YAML Format

```yaml
version: "1.0"

cards:
  - id: "unique_id"          # Unique identifier
    name: "Card Display Name" # Name shown to player
    type: monster             # monster, weapon, or health_potion
    value: 5                  # Numeric value (damage/healing/weapon power)
    count: 2                  # Number of copies in dungeon
    description: "Optional"   # Optional description (future use)
```

## Example Custom Dungeon

```yaml
version: "1.0"

cards:
  # Monsters
  - id: "rat"
    name: "Giant Rat"
    type: monster
    value: 2
    count: 4

  - id: "zombie"
    name: "Zombie"
    type: monster
    value: 5
    count: 3

  - id: "vampire"
    name: "Vampire Lord"
    type: monster
    value: 12
    count: 2

  # Weapons
  - id: "stick"
    name: "Wooden Stick"
    type: weapon
    value: 3
    count: 2

  - id: "hammer"
    name: "War Hammer"
    type: weapon
    value: 7
    count: 2

  # Potions
  - id: "potion_small"
    name: "Small Potion"
    type: health_potion
    value: 4
    count: 3

  - id: "potion_large"
    name: "Large Potion"
    type: health_potion
    value: 8
    count: 2
```

## Dungeon API

### Loading a Dungeon

```python
from pathlib import Path
from pyscoundrel.dungeon import Dungeon

# Load from custom file
dungeon = Dungeon(config_path=Path("my_dungeon.yaml"))

# Validate configuration
errors = dungeon.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")

# Get dungeon stats
print(f"Total cards: {dungeon.get_total_cards()}")
print(f"Monsters: {len(dungeon.get_cards_by_type(CardType.MONSTER))}")
print(f"Weapons: {len(dungeon.get_cards_by_type(CardType.WEAPON))}")
print(f"Potions: {len(dungeon.get_cards_by_type(CardType.HEALTH_POTION))}")
```

### Creating a Deck from Dungeon

```python
from pyscoundrel.models import Deck

# Create shuffled deck from dungeon
deck = Deck.from_dungeon(dungeon, shuffle=True, seed=42)

print(f"Deck size: {deck.remaining} cards")
```

## Card Balance Guidelines

For a balanced dungeon, consider:

1. **Total Cards**: 40-50 cards recommended
2. **Monster Distribution**:
   - Low (2-5): 30-40%
   - Mid (6-10): 40-50%
   - High (11-13): 10-20%
3. **Weapons**: ~20% of total (values 2-10)
4. **Potions**: ~20% of total (values 2-10)

## Playing Card vs Dungeon Mode

**Playing Card Mode** (legacy):
- Uses standard 52-card deck rules
- Suits determine card types
- Face cards map to values 11-14

**Dungeon Mode** (new):
- Custom card names
- No suit/rank references
- Full control over card distribution
- Thematic card naming

## CLI Usage

```bash
# Use default dungeon
python -m pyscoundrel

# Use custom dungeon
python -m pyscoundrel --dungeon path/to/dungeon.yaml

# With other options
python -m pyscoundrel --dungeon custom.yaml --seed 12345 --no-title
```

## Migration from Playing Cards

The Card model now supports both formats:

```python
# Legacy format (still works)
from pyscoundrel.models import Card, Rank, Suit
card = Card.from_playing_card(Rank.JACK, Suit.CLUBS)

# New format
card = Card.from_dungeon_card(
    card_id="orc_warrior",
    name="Orc Warrior",
    card_type=CardType.MONSTER,
    value=11
)
```

Both formats work seamlessly in the game engine!
