# PyScoundrel Quick Start Guide

## Installation ✅

```bash
# Clone and install
git clone https://github.com/yourusername/pyscoundrel.git
cd pyscoundrel
pip install -r requirements.txt
```

## Play the Game 🎮

```bash
# Basic game
python -m pyscoundrel

# With specific seed for reproducible game
python -m pyscoundrel --seed 42

# Skip title screen
python -m pyscoundrel --no-title

# Use custom dungeon
python -m pyscoundrel --dungeon my_dungeon.yaml
```

## Game Controls 🎯

**In-Game Menu:**
- Enter a number (1, 2, 3...) to select an action
- Enter **0** to quit game (counts as defeat)
- All choices are numbered - no letter inputs

**Menu Flow:**
- Avoid room (if available)
- Face cards (one choice per card)
- For monsters: Barehanded and Weapon options shown separately
- Fast flow - no confirmations, no pauses

## Game Mechanics Summary 🎲

**Card Types:**
- **Monsters**: Deal damage = card value (2-14)
- **Weapons**: Reduce monster damage. After a kill, can only kill monsters ≤ last kill value
- **Potions**: Heal (max 20 HP, one per turn)

**Flow:**
1. Draw 4 cards → Room
2. Face 3 of 4 cards (1 carries to next room)
3. Can avoid room (cards go to bottom), but not twice in a row
4. Win: Clear all 44 cards
5. Lose: Health reaches 0
6. Quit: Press 0 anytime

**Scoring:**
- Victory: Remaining health
- Defeat: -(sum of remaining monster damage)

## Dungeon Configuration 🏰

Customize your card pool with YAML:

```yaml
# custom_dungeon.yaml
version: "1.0"

cards:
  - id: "Dragon"
    name: "Dragon"
    type: monster
    value: 13
    count: 2

  - id: "Sword"
    name: "Steel Sword"
    type: weapon
    value: 7
    count: 1

  - id: "Potion"
    name: "Healing Potion"
    type: health_potion
    value: 5
    count: 3
```

See [DUNGEON_CONFIGURATION.md](DUNGEON_CONFIGURATION.md) for details.

## Programmatic Usage 💻

```python
from pyscoundrel.game.engine import GameEngine
from pyscoundrel.dungeon import Dungeon

# Create game
engine = GameEngine(seed=42)
engine.start_game()

# Game loop
while not engine.is_game_over:
    result = engine.draw_room()
    if result.metadata and result.metadata.get("game_over"):
        break

    # Face cards (your logic here)
    result = engine.face_card(0)

    # Handle monsters
    if result.metadata and "monster" in result.metadata:
        monster = result.metadata["monster"]
        if result.metadata.get("can_use_weapon"):
            engine.fight_monster_with_weapon(monster)
        else:
            engine.fight_monster_barehanded(monster)

# Get score
print(f"Victory: {engine.state.victory}")
print(f"Score: {engine.state.score}")
```

## Package Structure 📦

```
pyscoundrel/
├── models/          # Card, Deck, Weapon, Player, Room
├── game/            # GameEngine, GameState, Actions
├── dungeon/         # Card pool system with YAML configs
├── ui/              # Rich-based terminal interface
└── config.py        # Game configuration
```

## Need Help? 📖

- Full documentation: [README.md](README.md)
- Dungeon system: [DUNGEON_CONFIGURATION.md](DUNGEON_CONFIGURATION.md)
- Official rules: [official_rules.pdf](official_rules.pdf)

---

**Have fun dungeon crawling! 🃏⚔️**
