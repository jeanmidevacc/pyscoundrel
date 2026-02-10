# PyScoundrel 🃏

A Python implementation of **Scoundrel**, a single-player roguelike card game by Zach Gage and Kurt Bieg.

Experience the thrill of dungeon crawling through a deck of cards with a modern, clean terminal interface!

## 🎮 Features

- **Full Scoundrel Implementation**: Complete game mechanics including weapons, monsters, and health potions
- **Modern CLI Interface**: Clean terminal UI powered by Rich with:
  - Rounded borders and clean tables
  - Integer-based menu system (1, 2, 3... 0 to quit)
  - Color-coded cards by type
  - Health percentage display
  - Damage calculations shown clearly
- **Fast Flow Gameplay**: No pauses or confirmations - continuous action
- **Smart Choices**: Only valid actions are displayed (no disabled options)
- **Configurable Dungeons**: YAML-based card pool system - customize or create themed dungeons
- **Agent Support**: Create automated players with custom strategies
- **Comprehensive Logging**: Track every game event with JSON logs for analysis
  - Console logging for real-time monitoring
  - File logging with complete game state
  - Auto-generated filenames with timestamps
- **Reproducible Games**: Random seed support for consistent playthroughs

## 📦 Installation

### From source

```bash
git clone https://github.com/yourusername/pyscoundrel.git
cd pyscoundrel
pip install -r requirements.txt
```

### Dependencies

- Python 3.8+
- rich >= 13.0.0
- pyyaml >= 6.0.0

## 🎯 Quick Start

### Play the game

```bash
# Run with default settings
python -m pyscoundrel

# Use a specific random seed (for reproducible games)
python -m pyscoundrel --seed 42

# Skip title screen
python -m pyscoundrel --no-title

# Use a custom dungeon
python -m pyscoundrel --dungeon my_dungeon.yaml
```

### Command-line options

```bash
--seed INT           # Random seed for reproducible games
--no-title           # Skip title screen
--dungeon PATH       # Path to custom dungeon YAML
```

## 🎲 How to Play

### Game Rules

Scoundrel is played with a 44-card dungeon deck (26 monsters, 9 weapons, 9 potions).

**Card Types:**
- **Monsters**: Deal damage equal to their value (2-14)
- **Weapons**: Reduce monster damage. **Important weapon rule**: After killing a monster, the weapon can only be used on monsters ≤ last kill value
- **Health Potions**: Restore health (max 20 HP). One per turn only

**Gameplay:**
1. Draw 4 cards to form a **Room**
2. Choose to **avoid** the room (cards go to bottom of deck) or face it
   - Cannot avoid two rooms in a row
3. If facing the room, choose 3 of 4 cards to face (one carries over to next room)
4. Handle each card:
   - **Weapon**: Equip it (discards old weapon)
   - **Potion**: Heal (max 20 HP, one per turn)
   - **Monster**: Fight barehanded OR with weapon (if available)

**Winning/Losing:**
- **Win**: Clear the entire deck while staying alive
- **Lose**: Health reaches 0
- **Quit**: Press 0 anytime (counts as defeat)

**Scoring:**
- **Victory**: Your remaining health
- **Defeat**: Negative value = sum of remaining monster damage

## 🏰 Dungeon Configuration

PyScoundrel uses a YAML-based dungeon system for complete card customization.

### Default Dungeon

The default dungeon uses standard playing card names (J♣, 7♥, K♠, etc.) matching classic Scoundrel.

### Custom Dungeons

Create your own themed dungeons:

```yaml
# my_dungeon.yaml
version: "1.0"

cards:
  # Monsters
  - id: "Goblin"
    name: "Goblin"
    type: monster
    value: 3
    count: 4

  - id: "Dragon"
    name: "Dragon"
    type: monster
    value: 13
    count: 2

  # Weapons
  - id: "Sword"
    name: "Steel Sword"
    type: weapon
    value: 7
    count: 1

  # Potions
  - id: "Potion"
    name: "Healing Potion"
    type: health_potion
    value: 5
    count: 3
```

See [DUNGEON_CONFIGURATION.md](DUNGEON_CONFIGURATION.md) for full documentation.

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get playing in 2 minutes
- **[Dungeon Configuration](DUNGEON_CONFIGURATION.md)** - Customize your card pool with YAML
- **[Logging Guide](LOGGING.md)** - Track and analyze game events
- **[Agent Development](examples/README.md)** - Create automated players

## 🏗️ Package Structure

```
pyscoundrel/
├── models/          # Core game entities
│   ├── card.py      # Card model (supports both legacy and dungeon formats)
│   ├── deck.py      # Deck management with dungeon support
│   ├── weapon.py    # Weapon with kill history tracking
│   ├── player.py    # Player state (health, equipped weapon)
│   └── room.py      # Room with 4 cards
├── game/            # Game logic
│   ├── state.py     # GameState and GamePhase
│   ├── engine.py    # Core game logic and rules
│   └── actions.py   # Player actions and results
├── dungeon/         # Dungeon card pool system
│   ├── card_pool.py # Dungeon loader and validator
│   └── default_dungeon.yaml  # Default card pool
├── ui/              # Rich-based terminal UI
│   ├── renderer.py  # Game renderer
│   ├── theme.py     # Color theme
│   └── input.py     # Input handling
└── config.py        # Game configuration
```

## 💻 Programmatic Usage

Use PyScoundrel as a library:

```python
from pyscoundrel.game.engine import GameEngine
from pyscoundrel.dungeon import Dungeon
from pyscoundrel.config import GameConfig

# Create game with default dungeon
engine = GameEngine(seed=42)
engine.start_game()

# Or use a custom dungeon
dungeon = Dungeon(config_path="my_dungeon.yaml")
engine = GameEngine(dungeon=dungeon, seed=42)

# Game loop
while not engine.is_game_over:
    result = engine.draw_room()
    # Handle room...
    result = engine.face_card(0)
    # Handle card...

# Get final score
print(f"Victory: {engine.state.victory}")
print(f"Final Score: {engine.state.score}")
```

## 🎨 UI Features

**Modern Interface:**
- Numbered menu system (1-5 for actions, 0 to quit)
- Rounded borders and clean tables
- Color-coded card types
- Health bar with percentage
- Weapon status with restrictions

**Smart Display:**
- Monster combat options expanded in menu (barehanded + weapon as separate choices)
- Only valid choices shown (no grayed-out disabled options)
- Immediate feedback - no pauses between actions

**Fast Flow:**
- No "Press Enter to continue" prompts
- No quit confirmations
- Continuous gameplay

## 📝 License

This implementation is released under the MIT License. The original Scoundrel game is © 2011 Zach Gage and Kurt Bieg.

## 🙏 Credits

- **Original Game Design**: Zach Gage and Kurt Bieg
- **Python Implementation**: PyScoundrel Contributors
- **UI Library**: [Rich](https://github.com/Textualize/rich) by Will McGugan

## 🤝 Contributing

Contributions are welcome! This package focuses on clean game logic implementation with a modern CLI experience.

---

**Enjoy dungeon crawling through a deck of cards! 🃏⚔️**
